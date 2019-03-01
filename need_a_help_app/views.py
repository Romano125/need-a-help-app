from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.http import HttpResponse
from django.views import generic
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from user.models import (
    Profile,
    UserFavourite,
    Requests,
    SeenRequest,
    Hire,
    RepairmanRequests,
    Appliccation,
    JobHire
)
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)


def home(request):
    return render(request, 'need_a_help_app/index.html')


class AppMainView(LoginRequiredMixin, ListView):
    template_name = 'need_a_help_app/app_main.html'
    context_object_name = 'users'
    paginate_by = 3

    def get_queryset(self):
        return User.objects.all()

    def get_context_data(self, **kwargs):
        context_data = super(AppMainView, self).get_context_data(**kwargs)

        us = self.request.user
        reqq_seen = SeenRequest.objects.filter(user=us)

        hired = Hire.objects.filter(user=us)
        uss = User.objects.all()

        f_hired = []
        for u in uss:
            for h in hired:
                if h.user == us and h.repairman == u.id and h.status == 'pending':
                    f_hired.append(u)

        context_data['f_hired'] = f_hired
        context_data['seen_r'] = reqq_seen
        context_data['cnt'] = self.request.session.get('cnt')

        return context_data


class InfoDetailView(LoginRequiredMixin, DetailView):
    model = User
    context_object_name = 'info'
    template_name = 'user/info.html'

    def get_context_data(self, **kwargs):
        context_data = super(InfoDetailView, self).get_context_data(**kwargs)

        rep_id = self.kwargs['pk']
        user = self.request.user
        favs = UserFavourite.objects.all()

        f = 0
        for us in favs:
            if us.user == user.id and us.repairman == rep_id:
                f = 1

        hired = Hire.objects.all()
        f_hired = 0
        for h in hired:
            if h.user == user and h.repairman == rep_id and h.status == 'pending':
                f_hired = 1

        context_data['f'] = f
        context_data['f_hired'] = f_hired

        return context_data


class UpdateUserView(LoginRequiredMixin, UpdateView):
    model = Profile
    context_object_name = 'repairman'
    fields = [
        'email',
        'address',
        'birth_date',
        'phone_number',
        'profession',
        'knowledges',
        'photo'
    ]

    success_url = reverse_lazy('main')


@login_required
def add_favorite(request, user_id, rep_id):
    f = 0
    favs = UserFavourite.objects.all()
    for us in favs:
        if us.user == user_id and us.repairman == rep_id:
            f = 1

    if f == 0:
        add_fav = UserFavourite(user=user_id, repairman=rep_id)
        add_fav.save()

    return redirect('info', pk=rep_id)


@login_required
def del_favorite(request, user_id, rep_id):
    f = 0
    favs = UserFavourite.objects.all()
    for us in favs:
        if us.user == user_id and us.repairman == rep_id:
            fav_to_del = UserFavourite.objects.filter(user=user_id, repairman=rep_id)
            f = 1

    if f == 1:
        fav_to_del.delete()

    return redirect('info', pk=rep_id)


@login_required
def show_favs(request):
    favs = UserFavourite.objects.all()
    users = User.objects.all()

    context = {
        'favs': favs,
        'users': users
    }
    return render(request, 'need_a_help_app/favorites.html', context)


class RequestsView(LoginRequiredMixin, ListView):
    model = Requests
    template_name = 'user/requests_user.html'
    context_object_name = 'req'
    paginate_by = 2

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs.get('pk'))
        return Requests.objects.filter(user=user).order_by('-date')


class RequestCreateView(LoginRequiredMixin, CreateView):
    model = Requests
    fields = [
        'job_title',
        'price',
        'required_knowledges',
        'address',
        'job_description',
        'photo'
    ]

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class RequestDetailView(LoginRequiredMixin, DetailView):
    model = Requests
    template_name = 'user/requests_detail.html'

    def get_context_data(self, **kwargs):
        context_data = super(RequestDetailView, self).get_context_data(**kwargs)

        req_id = self.kwargs['pk']
        user_log = self.request.user
        req = Requests.objects.filter(id=req_id)
        reqq_seen = SeenRequest.objects.all()
        us = User.objects.all()

        f = 0
        for r in reqq_seen:
            if r.user == user_log and req_id == r.request.id and not r.seen:
                req_to_save = r
                f = 1

        c = 0
        if user_log.profile.role == 'client':
            for u in us:
                for r in reqq_seen:
                    if r.user == u and req_id == r.request.id:
                        c += 1

            if c != us.count() and f == 0:
                for u in us:
                    seen_req = SeenRequest(user=u, request=req.first(), seen=False)
                    seen_req.save()
            f = 2

        if f == 1:
            req_to_save.seen = True
            req_to_save.save()

        app = Appliccation.objects.filter(request=req.first())
        cnt = Appliccation.objects.filter(request=req.first()).count()
        vis = Requests.objects.filter(id=req_id).first()

        context_data['s'] = reqq_seen
        context_data['app'] = app
        context_data['cnt'] = cnt
        context_data['vis'] = vis.visible

        return context_data


class RequestUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Requests
    fields = [
        'job_title',
        'price',
        'required_knowledges',
        'address',
        'job_description',
        'photo'
    ]

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def test_func(self):
        req = self.get_object()
        if self.request.user == req.user:  # ako je ulogirani user isti kao onaj ciji post mijenjamo, ne zelimo da netko drugi ureduje sve druge postove
            return True
        return False


class RequestDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Requests

    def test_func(self):
        req = self.get_object()
        if self.request.user == req.user:  # ako je ulogirani user isti kao onaj ciji post mijenjamo, ne zelimo da netko drugi ureduje sve druge postove
            return True
        return False

    def get_success_url(self):
        user = self.object.user
        return reverse_lazy('requests_user', kwargs={'pk': user.id})

    def delete(self, request, *args, **kwargs):
        messages.success(request, f'You\'ve deleted posted request successfuly!')
        return super(RequestDeleteView, self).delete(request, *args, **kwargs)


@login_required
def search(request):
    q = request.GET.get('q')
    users = User.objects.all()
    if q:
        prof = Profile.objects.filter(Q(profession__contains=q))

    f = 0
    if prof:
        f = 1

    """
    us = User.objects.filter(id=selfrequest.user)
    hired = Hire.objects.filter(user=us)

    f_hired = []
    for u in users:
        for h in hired:
            if h.user == us and h.repairman == u.id and h.status == 'pending':
                f_hired.append(u)
    """

    return render(request, 'need_a_help_app/search_results.html', {'users': users, 'q': q, 'f': f, 'prof': prof})


@login_required
def hire_repairman(request, user_id, rep_id):
    f = 0
    hired = Hire.objects.all()
    for h in hired:
        if h.user.id == user_id and h.repairman == rep_id and h.status == 'pending':
            f = 1

    us = User.objects.filter(id=user_id).first()
    rep = User.objects.filter(id=rep_id).first()
    if f == 0:
        hire_rep = Hire(user=us, repairman=rep_id)
        hire_rep.save()
        mess = us.username + ' needs your help in solving a problem!'
        req_mess = RepairmanRequests(repairman=rep, user=user_id, request_message=mess)
        req_mess.save()

    messages.success(request, f'You\'ve hired repairman successfuly! Wait him to accept!')
    return redirect('info', pk=rep_id)


class HiredListView(LoginRequiredMixin, ListView):
    model = Hire
    template_name = 'need_a_help_app/hired_user.html'
    context_object_name = 'hir'
    paginate_by = 2

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs.get('pk'))
        return Hire.objects.filter(user=user).order_by('-date')

    def get_context_data(self, **kwargs):
        context_data = super(HiredListView, self).get_context_data(**kwargs)

        users = User.objects.all()
        job = JobHire.objects.order_by('-date_hired')

        context_data['us'] = users
        context_data['job'] = job

        return context_data


class RepairmanRequestsListView(LoginRequiredMixin, ListView):
    model = RepairmanRequests
    template_name = 'need_a_help_app/requests_repairman.html'
    context_object_name = 'req_rep'
    paginate_by = 2

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs.get('pk'))
        return RepairmanRequests.objects.filter(repairman=user, seen=False).order_by('-date')

    def get_context_data(self, **kwargs):
        context_data = super(RepairmanRequestsListView, self).get_context_data(**kwargs)

        users = User.objects.all()
        us = self.request.user
        req = RepairmanRequests.objects.filter(repairman=us, seen=False).count()

        context_data['us'] = users
        context_data['cnt'] = req
        self.request.session['cnt'] = req

        return context_data


@login_required
def job_accept(request, user_id, rep_id):
    users = User.objects.all()
    rep_req = RepairmanRequests.objects.filter(user=user_id).order_by('-date')

    for i in rep_req:
        f = 0
        for j in users:
            if i.repairman == j:
                i.seen = True
                i.active = True
                i.save()
                f = 1
        if f:
            break

    us = User.objects.filter(id=user_id).first()
    hir = Hire.objects.filter(user=us, repairman=rep_id).order_by('-date').first()
    hir.accepted = True
    hir.save()

    messages.success(request, f'You\'ve accepted a job from { us.username }!')
    return redirect('active_repairman', pk=rep_id)


class RepairmanActiveListView(LoginRequiredMixin, ListView):
    model = RepairmanRequests
    template_name = 'need_a_help_app/active_repairman.html'
    context_object_name = 'act_rep'
    paginate_by = 2

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs.get('pk'))
        return RepairmanRequests.objects.filter(repairman=user, active=True).order_by('-date')

    def get_context_data(self, **kwargs):
        context_data = super(RepairmanActiveListView, self).get_context_data(**kwargs)

        users = User.objects.all()
        us = self.request.user
        job = JobHire.objects.filter(repairman=us, status='pending')

        context_data['us'] = users
        context_data['job'] = job

        return context_data


@login_required
def job_done(request, user_id, rep_id):
    users = User.objects.all()
    rep_req = RepairmanRequests.objects.filter(user=user_id).order_by('-date')

    for i in rep_req:
        f = 0
        for j in users:
            if i.repairman == j:
                i.active = False
                i.done = True
                i.save()
                f = 1
        if f:
            break

    us = User.objects.filter(id=user_id).first()
    hir = Hire.objects.filter(user=us, repairman=rep_id).order_by('-date').first()
    hir.status = 'done'
    hir.save()

    messages.success(request, f'You\'ve finished a job for { us.username }!')
    return redirect('done_repairman', pk=rep_id)


class RepairmanDoneListView(LoginRequiredMixin, ListView):
    model = RepairmanRequests
    template_name = 'need_a_help_app/done_repairman.html'
    context_object_name = 'don_rep'
    paginate_by = 2

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs.get('pk'))
        return RepairmanRequests.objects.filter(repairman=user, done=True).order_by('-date')

    def get_context_data(self, **kwargs):
        context_data = super(RepairmanDoneListView, self).get_context_data(**kwargs)

        users = User.objects.all()
        us = self.request.user
        job_done = JobHire.objects.filter(repairman=us, status='done')

        context_data['us'] = users
        context_data['done'] = job_done

        return context_data


@login_required
def repairman_apply(request, us_id, req_id):
    us = User.objects.filter(id=us_id).first()
    req = Requests.objects.filter(id=req_id).first()
    app = Appliccation.objects.filter(repairman=us, request=req)

    if not app:
        app_save = Appliccation(repairman=us, request=req)
        app_save.save()
        messages.success(request, f'You\'ve successfuly applied for a job { req.job_title }!')
        return redirect('request_detail', pk=req.id)
    else:
        messages.warning(request, f'You\'ve already applied for a job { req.job_title }!')
        return redirect('request_detail', pk=req.id)


class RepairmanApplicationsListView(LoginRequiredMixin, ListView):
    model = Appliccation
    template_name = 'need_a_help_app/repairman_apps.html'
    context_object_name = 'app'
    paginate_by = 2

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs.get('pk'))
        return Appliccation.objects.filter(repairman=user)


@login_required
def posted_job_hire(request, us_id, req_id):
    us = User.objects.filter(id=us_id).first()
    req = Requests.objects.filter(id=req_id).first()
    job = JobHire.objects.filter(repairman=us, request=req)

    req.visible = False
    req.save()

    if not job:
        job_save = JobHire(repairman=us, request=req)
        job_save.save()
        messages.success(request, f'You\'ve hired { us.username } for a job { req.job_title }!')
        return redirect('hired_user', pk=req.user.id)


@login_required
def posted_job_done(request, us_id, req_id):
    us = User.objects.filter(id=us_id).first()
    req = Requests.objects.filter(id=req_id).first()
    job = JobHire.objects.filter(repairman=us, request=req).first()

    job.status = 'done'
    job.save()

    messages.success(request, f'You\'ve finished a job { req.job_title } for { req.user.username }!')
    return redirect('done_repairman', pk=us.id)


class JobHireDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Requests

    def test_func(self):
        req = self.get_object()
        if self.request.user == req.user:  # ako je ulogirani user isti kao onaj ciji post mijenjamo, ne zelimo da netko drugi ureduje sve druge postove
            return True
        return False

    def get_success_url(self):
        user = self.object.user
        return reverse_lazy('hired_user', kwargs={'pk': user.id})

    def delete(self, request, *args, **kwargs):
        messages.success(request, f'You\'ve deleted posted request where you hired a repairman successfuly!')
        return super(JobHireDeleteView, self).delete(request, *args, **kwargs)


def cancel_application(request, user_id, req_id):
    us = User.objects.filter(id=user_id).first()
    req = Requests.objects.filter(id=req_id).first()
    Appliccation.objects.filter(repairman=us, request=req).delete()

    messages.success(request, f'You\'ve quit the job { req.job_title } that you have been applied for!')
    return redirect('repairman_apps', pk=us.id)


def client_repairman_job_delete(request, user_id, rep_id, log_id, txt):
    us = User.objects.filter(id=user_id).first()
    hir = Hire.objects.filter(user=us, repairman=rep_id)

    for h in hir:
        if h.status == 'pending':
            h.delete()
            break

    rep = User.objects.filter(id=rep_id).first()
    req = RepairmanRequests.objects.filter(repairman=rep, user=user_id)

    log = User.objects.filter(id=log_id).first()

    for r in req:
        if not r.done:
            r.delete()
            break

    if log.profile.role == 'client':
        messages.success(request, f'You\'ve canceled the job for which you hired { rep.username }!')
        return redirect('hired_user', pk=log.id)
    else:
        messages.success(request, f'You quit the job for which you were hired by { us.username }!')
        if txt == 'req':
            return redirect('requests_repairman', pk=rep_id)
        elif txt == 'act':
            return redirect('active_repairman', pk=rep_id)
