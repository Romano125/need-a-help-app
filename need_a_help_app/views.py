from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views import generic
from user.models import Profile, UserFavourite, Requests
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, 'need_a_help_app/index.html')


class AppMainView(LoginRequiredMixin, ListView):
    template_name = 'need_a_help_app/app_main.html'
    context_object_name = 'users'
    paginate_by = 3

    def get_queryset(self):
        return User.objects.all()


class RepairmanDetailView(LoginRequiredMixin, DetailView):
    model = User
    context_object_name = 'repairman'
    template_name = 'user/repairman_info.html'

    def get_context_data(self, **kwargs):
        context_data = super(RepairmanDetailView, self).get_context_data(**kwargs)

        rep_id = self.kwargs['pk']
        user = self.request.user
        favs = UserFavourite.objects.all()

        f = 0
        for us in favs:
            if us.user == user.id and us.repairman == rep_id:
                f = 1

        context_data['f'] = f

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

    return redirect('repairman_info', pk=rep_id)


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

    return redirect('repairman_info', pk=rep_id)


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
    success_url = reverse_lazy('main')

    def test_func(self):
        req = self.get_object()
        if self.request.user == req.user:  # ako je ulogirani user isti kao onaj ciji post mijenjamo, ne zelimo da netko drugi ureduje sve druge postove
            return True
        return False
