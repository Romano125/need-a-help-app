import os
import json
import urllib.request, urllib.parse
from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.http import HttpResponse, Http404
from django.views import generic
from django.contrib.auth.models import User
from django.urls import reverse_lazy, reverse
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
    JobHire,
    ClientNotifications,
    RepairmanNotifications,
    Rate,
    RequestImages,
    ClientMessage
)
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from user.forms import RequestsForm
from need_a_help import settings
from .filters import MostWantedFilter, TopRatedFilter, FavouritesFilter, SearchFilter
#from storages.backends.s3boto3 import S3Boto3Storage, SpooledTemporaryFile

"""
class CustomS3Boto3Storage(S3Boto3Storage):

    def _save_content(self, obj, content, parameters):

        #We create a clone of the content file as when this is passed to boto3 it wrongly closes
        #the file upon upload where as the storage backend expects it to still be open

        # Seek our content back to the start
        content.seek(0, os.SEEK_SET)

        # Create a temporary file that will write to disk after a specified size
        content_autoclose = SpooledTemporaryFile()

        # Write our original content into our copy that will be closed by boto3
        content_autoclose.write(content.read())

        # Upload the object which will auto close the content_autoclose instance
        super(CustomS3Boto3Storage, self)._save_content(obj, content_autoclose, parameters)

        # Cleanup if this is fixed upstream our duplicate should always close
        if not content_autoclose.closed:
            content_autoclose.close()

"""
api_key = settings.GOOGLE_MAPS_API_KEY


def home(request):
    return render(request, 'need_a_help_app/index.html')


def about(request):

    if request.user.is_authenticated:
        us = request.user
        not_c = ClientNotifications.objects.filter(client=us, remove=False).order_by('-date')
        not_cli = ClientNotifications.objects.filter(client=us, seen=False).count()

        cnt = RepairmanRequests.objects.filter(repairman=us, seen=False).count()
        not_r = RepairmanNotifications.objects.filter(repairman=us, remove=False).order_by('-date')
        not_rep = RepairmanNotifications.objects.filter(repairman=us, seen=False).count()
        mess_cli = ClientMessage.objects.filter((Q(client=us) | Q(sender=us)) & Q(seen=False)).order_by("-date")
        mess_cli_c = ClientMessage.objects.filter(Q(client=us) & Q(seen_notif=False)).count()

        context = {
            'cnt': cnt,
            'not_r': not_r,
            'not_rep': not_rep,
            'not_c': not_c,
            'not_cli': not_cli,
            'mess_cli': mess_cli,
            'mess_cli_c': mess_cli_c
        }

        return render(request, 'need_a_help_app/about.html', context)
    else:
        return render(request, 'need_a_help_app/about.html')


class AppMainClientView(LoginRequiredMixin, ListView):
    template_name = 'need_a_help_app/app_main_client.html'
    context_object_name = 'filter'
    paginate_by = 5

    def get_queryset(self):
        qs = Profile.objects.filter(role='repairman').order_by('-rating')
        return MostWantedFilter(self.request.GET, queryset=qs).qs

    def get_context_data(self, **kwargs):
        context_data = super(AppMainClientView, self).get_context_data(**kwargs)

        us = self.request.user

        hired = Hire.objects.filter(user=us)
        uss = User.objects.all()

        f_hired = []
        for u in uss:
            for h in hired:
                if h.user == us and h.repairman == u.id and h.status == 'pending':
                    f_hired.append(u)

        not_c = ClientNotifications.objects.filter(client=us, remove=False).order_by('-date')
        not_cli = ClientNotifications.objects.filter(client=us, seen=False).count()
        mess_cli = ClientMessage.objects.filter((Q(client=us) | Q(sender=us)) & Q(seen=False)).order_by("-date")
        mess_cli_c = ClientMessage.objects.filter(Q(client=us) & Q(seen_notif=False)).count()

        origin = us.profile.address
        distance = {}
        for users in uss:
            if users.profile.role == 'repairman':
                dist = '-'
                api = urllib.request.urlopen(f'https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins={ urllib.parse.quote(origin) }&destinations={ urllib.parse.quote(users.profile.address) }&key={ api_key }').read(1000)
                data = json.loads(api.decode('utf-8'))
                if data['rows'][0]['elements'][0]['status'] == 'OK':
                    dist = data['rows'][0]['elements'][0]['distance']['text']

                distance.update({users.id: dist})

        context_data['f_hired'] = f_hired
        context_data['not_c'] = not_c
        context_data['not_cli'] = not_cli
        context_data['dist'] = distance
        context_data['filter_form'] = MostWantedFilter(self.request.GET, queryset=self.get_queryset())
        context_data['mess_cli'] = mess_cli
        context_data['mess_cli_c'] = mess_cli_c

        return context_data


class AppMainRepairmanView(LoginRequiredMixin, ListView):
    template_name = 'need_a_help_app/app_main_repairman.html'
    context_object_name = 'req'
    paginate_by = 5

    def get_queryset(self):
        return Requests.objects.filter(visible=True).order_by('-date')

    def get_context_data(self, **kwargs):
        context_data = super(AppMainRepairmanView, self).get_context_data(**kwargs)

        us = self.request.user
        reqq_seen = SeenRequest.objects.filter(user=us)

        req = Requests.objects.filter(visible=True)

        cnt = RepairmanRequests.objects.filter(repairman=us, seen=False).count()
        act_job = RepairmanRequests.objects.filter(repairman=us, active=True, done=False).count()
        act_req = JobHire.objects.filter(repairman=us, status='pending').count()
        act_cnt = act_job + act_req
        not_r = RepairmanNotifications.objects.filter(repairman=us, remove=False).order_by('-date')
        not_rep = RepairmanNotifications.objects.filter(repairman=us, seen=False).count()
        mess_cli = ClientMessage.objects.filter((Q(client=us) | Q(sender=us)) & Q(seen=False)).order_by("-date")
        mess_cli_c = ClientMessage.objects.filter(Q(client=us) & Q(seen_notif=False)).count()

        origin = us.profile.address
        distance = {}
        for r in req:
            dist = '-'
            api = urllib.request.urlopen(f'https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins={ urllib.parse.quote(origin) }&destinations={ urllib.parse.quote(r.address) }&key={ api_key }').read(1000)
            data = json.loads(api.decode('utf-8'))
            if data['rows'][0]['elements'][0]['status'] == 'OK':
                dist = data['rows'][0]['elements'][0]['distance']['text']

            distance.update({r.id: dist})

        context_data['seen_r'] = reqq_seen
        context_data['cnt'] = cnt
        context_data['act_cnt'] = act_cnt
        context_data['not_r'] = not_r
        context_data['not_rep'] = not_rep
        context_data['dist'] = distance
        context_data['mess_cli'] = mess_cli
        context_data['mess_cli_c'] = mess_cli_c


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

        get_not = self.request.GET.get('not', -1)
        get_not_c = self.request.GET.get('not_c', -1)

        if get_not != -1:
            not_seen = RepairmanNotifications.objects.filter(id=get_not).first()
            not_seen.seen = True
            not_seen.save()

        if get_not_c != -1:
            not_seen = ClientNotifications.objects.filter(id=get_not_c).first()
            not_seen.seen = True
            not_seen.save()

        us = self.request.user
        not_r = RepairmanNotifications.objects.filter(repairman=us, remove=False).order_by('-date')
        not_c = ClientNotifications.objects.filter(client=us, remove=False).order_by('-date')
        mess_cli = ClientMessage.objects.filter((Q(client=us) | Q(sender=us)) & Q(seen=False)).order_by("-date")
        mess_cli_c = ClientMessage.objects.filter(Q(client=us) & Q(seen_notif=False)).count()
        not_rep = RepairmanNotifications.objects.filter(repairman=us, seen=False).count()
        not_cli = ClientNotifications.objects.filter(client=us, seen=False).count()
        feeds = Rate.objects.all().order_by('-date')

        rep = User.objects.filter(id=rep_id).first()
        num_rates = Rate.objects.filter(repairman=rep).count()
        five_num = Rate.objects.filter(repairman=rep, rate=5).count()
        four_num = Rate.objects.filter(repairman=rep, rate=4).count()
        three_num = Rate.objects.filter(repairman=rep, rate=3).count()
        two_num = Rate.objects.filter(repairman=rep, rate=2).count()
        one_num = Rate.objects.filter(repairman=rep, rate=1).count()

        if five_num and num_rates:
            five_per = (five_num / num_rates) * 100
        else:
            five_per = 0
        if four_num and num_rates:
            four_per = (four_num / num_rates) * 100
        else:
            four_per = 0
        if three_num and num_rates:
            three_per = (three_num / num_rates) * 100
        else:
            three_per = 0
        if two_num and num_rates:
            two_per = (two_num / num_rates) * 100
        else:
            two_per = 0
        if one_num and num_rates:
            one_per = (one_num / num_rates) * 100
        else:
            one_per = 0

        origin = us.profile.address
        api = urllib.request.urlopen(f'https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins={ urllib.parse.quote(origin) }&destinations={ urllib.parse.quote(rep.profile.address) }&key={ api_key }').read(1000)
        data = json.loads(api.decode('utf-8'))
        dist = '-'
        if data['rows'][0]['elements'][0]['status'] == 'OK':
            dist = data['rows'][0]['elements'][0]['distance']['text']

        context_data['f'] = f
        context_data['f_hired'] = f_hired
        context_data['not_r'] = not_r
        context_data['not_c'] = not_c
        context_data['not_rep'] = not_rep
        context_data['not_cli'] = not_cli
        context_data['feeds'] = feeds
        context_data['num_rates'] = num_rates
        context_data['five_per'] = five_per
        context_data['four_per'] = four_per
        context_data['three_per'] = three_per
        context_data['two_per'] = two_per
        context_data['one_per'] = one_per
        context_data['dist'] = dist
        context_data['mess_cli'] = mess_cli
        context_data['mess_cli_c'] = mess_cli_c

        return context_data


class ModalInfoDetailView(LoginRequiredMixin, DetailView):
    model = User
    context_object_name = 'modal_info'
    template_name = 'user/modal_info.html'

    def get_context_data(self, **kwargs):
        context_data = super(ModalInfoDetailView, self).get_context_data(**kwargs)

        rep_id = self.kwargs['pk']
        user = self.request.user
        favs = UserFavourite.objects.all()

        f = 0
        for us in favs:
            if us.user == user.id and us.repairman == rep_id:
                f = 1

        us = self.request.user
        not_c = ClientNotifications.objects.filter(client=us, remove=False).order_by('-date')
        mess_cli = ClientMessage.objects.filter((Q(client=us) | Q(sender=us)) & Q(seen=False)).order_by("-date")
        mess_cli_c = ClientMessage.objects.filter(Q(client=us) & Q(seen_notif=False)).count()
        feeds = Rate.objects.all().order_by('-date')

        rep = User.objects.filter(id=rep_id).first()
        num_rates = Rate.objects.filter(repairman=rep).count()
        five_num = Rate.objects.filter(repairman=rep, rate=5).count()
        four_num = Rate.objects.filter(repairman=rep, rate=4).count()
        three_num = Rate.objects.filter(repairman=rep, rate=3).count()
        two_num = Rate.objects.filter(repairman=rep, rate=2).count()
        one_num = Rate.objects.filter(repairman=rep, rate=1).count()

        if five_num and num_rates:
            five_per = (five_num / num_rates) * 100
        else:
            five_per = 0
        if four_num and num_rates:
            four_per = (four_num / num_rates) * 100
        else:
            four_per = 0
        if three_num and num_rates:
            three_per = (three_num / num_rates) * 100
        else:
            three_per = 0
        if two_num and num_rates:
            two_per = (two_num / num_rates) * 100
        else:
            two_per = 0
        if one_num and num_rates:
            one_per = (one_num / num_rates) * 100
        else:
            one_per = 0

        origin = us.profile.address
        api = urllib.request.urlopen(f'https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins={ urllib.parse.quote(origin) }&destinations={ urllib.parse.quote(rep.profile.address) }&key={ api_key }').read(1000)
        data = json.loads(api.decode('utf-8'))
        dist = '-'
        if data['rows'][0]['elements'][0]['status'] == 'OK':
            dist = data['rows'][0]['elements'][0]['distance']['text']

        context_data['f'] = f
        context_data['not_c'] = not_c
        context_data['feeds'] = feeds
        context_data['num_rates'] = num_rates
        context_data['five_per'] = five_per
        context_data['four_per'] = four_per
        context_data['three_per'] = three_per
        context_data['two_per'] = two_per
        context_data['one_per'] = one_per
        context_data['dist'] = dist
        context_data['mess_cli'] = mess_cli
        context_data['mess_cli_c'] = mess_cli_c

        return context_data


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

    messages.success(request, f'You\'ve added repairman to favorites successfuly!')

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

    messages.warning(request, f'You\'ve deleted repairman from favorites!')

    return redirect('info', pk=rep_id)


@login_required
def show_favs(request):
    favs = UserFavourite.objects.all()
    users = User.objects.all()

    hired = Hire.objects.all()

    f_hired = []
    for u in favs:
        for h in hired:
            us = User.objects.filter(id=u.user).first()
            rep = User.objects.filter(id=u.repairman).first()
            if h.user == us and h.repairman == u.repairman and h.status == 'pending':
                f_hired.append(rep)

    us = request.user
    not_c = ClientNotifications.objects.filter(client=us, remove=False).order_by('-date')
    not_cli = ClientNotifications.objects.filter(client=us, seen=False).count()
    mess_cli = ClientMessage.objects.filter((Q(client=us) | Q(sender=us)) & Q(seen=False)).order_by("-date")
    mess_cli_c = ClientMessage.objects.filter(Q(client=us) & Q(seen_notif=False)).count()

    origin = us.profile.address
    distance = {}
    for u in users:
        if u.profile.role == 'repairman':
            dist = '-'
            api = urllib.request.urlopen(f'https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins={ urllib.parse.quote(origin) }&destinations={ urllib.parse.quote(u.profile.address) }&key={ api_key }').read(1000)
            data = json.loads(api.decode('utf-8'))
            if data['rows'][0]['elements'][0]['status'] == 'OK':
                dist = data['rows'][0]['elements'][0]['distance']['text']

            distance.update({u.id: dist})

    context = {
        'favs': favs,
        'users': users,
        'f_hired': f_hired,
        'not_c': not_c,
        'not_cli': not_cli,
        'dist': distance,
        'mess_cli': mess_cli,
        'mess_cli_c': mess_cli_c,
    }

    return render(request, 'need_a_help_app/favorites.html', context)


class RequestsView(LoginRequiredMixin, ListView):
    model = Requests
    template_name = 'user/requests_user.html'
    context_object_name = 'req'
    paginate_by = 4

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs.get('pk'))
        return Requests.objects.filter(user=user, visible=True).order_by('-date')

    def get_context_data(self, **kwargs):
        context_data = super(RequestsView, self).get_context_data(**kwargs)

        us = self.request.user
        not_c = ClientNotifications.objects.filter(client=us, remove=False).order_by('-date')
        not_cli = ClientNotifications.objects.filter(client=us, seen=False).count()
        mess_cli = ClientMessage.objects.filter((Q(client=us) | Q(sender=us)) & Q(seen=False)).order_by("-date")
        mess_cli_c = ClientMessage.objects.filter(Q(client=us) & Q(seen_notif=False)).count()

        context_data['not_c'] = not_c
        context_data['not_cli'] = not_cli
        context_data['mess_cli'] = mess_cli
        context_data['mess_cli_c'] = mess_cli_c

        return context_data


class RequestCreateView(LoginRequiredMixin, CreateView):
    model = Requests

    form_class = RequestsForm

    def form_valid(self, form):
        form.instance.user = self.request.user

        self.object = form.save()
        files = self.request.FILES.getlist('photo')
        for f in files:
            add_photo = RequestImages(request=self.object, photo=f)
            add_photo.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context_data = super(RequestCreateView, self).get_context_data(**kwargs)

        us = self.request.user
        not_c = ClientNotifications.objects.filter(client=us, remove=False).order_by('-date')
        not_cli = ClientNotifications.objects.filter(client=us, seen=False).count()
        mess_cli = ClientMessage.objects.filter((Q(client=us) | Q(sender=us)) & Q(seen=False)).order_by("-date")
        mess_cli_c = ClientMessage.objects.filter(Q(client=us) & Q(seen_notif=False)).count()

        context_data['not_c'] = not_c
        context_data['not_cli'] = not_cli
        context_data['mess_cli'] = mess_cli
        context_data['mess_cli_c'] = mess_cli_c
        context_data['api_key'] = settings.GOOGLE_MAPS_API_KEY

        return context_data


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

        get_not = self.request.GET.get('not', -1)
        get_not_c = self.request.GET.get('not_c', -1)

        if get_not != -1:
            not_seen = RepairmanNotifications.objects.filter(id=get_not).first()
            not_seen.seen = True
            not_seen.save()

        if get_not_c != -1:
            not_seen = ClientNotifications.objects.filter(id=get_not_c).first()
            not_seen.seen = True
            not_seen.save()

        us = self.request.user
        not_r = RepairmanNotifications.objects.filter(repairman=us, remove=False).order_by('-date')
        not_c = ClientNotifications.objects.filter(client=us, remove=False).order_by('-date')
        not_rep = RepairmanNotifications.objects.filter(repairman=us, seen=False).count()
        not_cli = ClientNotifications.objects.filter(client=us, seen=False).count()
        mess_cli = ClientMessage.objects.filter((Q(client=us) | Q(sender=us)) & Q(seen=False)).order_by("-date")
        mess_cli_c = ClientMessage.objects.filter(Q(client=us) & Q(seen_notif=False)).count()

        origin = us.profile.address
        api = urllib.request.urlopen(f'https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins={ urllib.parse.quote(origin) }&destinations={ urllib.parse.quote(req.first().address) }&key={ api_key }').read(1000)
        data = json.loads(api.decode('utf-8'))
        dist = '-'
        if data['rows'][0]['elements'][0]['status'] == 'OK':
            dist = data['rows'][0]['elements'][0]['distance']['text']

        uss = User.objects.all()
        distance = {}
        for u in uss:
            if u.profile.role == 'repairman':
                dist2 = '-'
                api = urllib.request.urlopen(f'https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins={ urllib.parse.quote(u.profile.address) }&destinations={ urllib.parse.quote(req.first().address) }&key={ api_key }').read(1000)
                data = json.loads(api.decode('utf-8'))
                if data['rows'][0]['elements'][0]['status'] == 'OK':
                    dist2 = data['rows'][0]['elements'][0]['distance']['text']

                distance.update({u.id: dist2})

        images = RequestImages.objects.filter(request=req.first())

        context_data['s'] = reqq_seen
        context_data['app'] = app
        context_data['cnt'] = cnt
        context_data['vis'] = vis.visible
        context_data['not_r'] = not_r
        context_data['not_c'] = not_c
        context_data['not_rep'] = not_rep
        context_data['not_cli'] = not_cli
        context_data['dist'] = dist
        context_data['dist2'] = distance
        context_data['images'] = images
        context_data['mess_cli'] = mess_cli
        context_data['mess_cli_c'] = mess_cli_c


        return context_data


class RequestUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Requests
    form_class = RequestsForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def test_func(self):
        req = self.get_object()
        if self.request.user == req.user:  # ako je ulogirani user isti kao onaj ciji post mijenjamo, ne zelimo da netko drugi ureduje sve druge postove
            return True
        return False

    def get_context_data(self, **kwargs):
        context_data = super(RequestUpdateView, self).get_context_data(**kwargs)

        us = self.request.user
        not_c = ClientNotifications.objects.filter(client=us, remove=False).order_by('-date')
        not_cli = ClientNotifications.objects.filter(client=us, seen=False).count()
        mess_cli = ClientMessage.objects.filter((Q(client=us) | Q(sender=us)) & Q(seen=False)).order_by("-date")
        mess_cli_c = ClientMessage.objects.filter(Q(client=us) & Q(seen_notif=False)).count()

        context_data['not_c'] = not_c
        context_data['not_cli'] = not_cli
        context_data['mess_cli'] = mess_cli
        context_data['mess_cli_c'] = mess_cli_c
        context_data['api_key'] = settings.GOOGLE_MAPS_API_KEY

        return context_data

    def post(self, request, *args, **kwargs):
        req = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('photo')
        if form.is_valid():
            for f in files:
                add_photo = RequestImages(request=req, photo=f)
                add_photo.save()
            req.photo = files[0]
            req.save()
            return redirect('request_detail', pk=req.id)


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

    def get_context_data(self, **kwargs):
        context_data = super(RequestDeleteView, self).get_context_data(**kwargs)

        us = self.request.user
        not_c = ClientNotifications.objects.filter(client=us, remove=False).order_by('-date')
        not_cli = ClientNotifications.objects.filter(client=us, seen=False).count()
        mess_cli = ClientMessage.objects.filter((Q(client=us) | Q(sender=us)) & Q(seen=False)).order_by("-date")
        mess_cli_c = ClientMessage.objects.filter(Q(client=us) & Q(seen_notif=False)).count()

        context_data['not_c'] = not_c
        context_data['not_cli'] = not_cli
        context_data['mess_cli'] = mess_cli
        context_data['mess_cli_c'] = mess_cli_c


        return context_data

    def delete(self, request, *args, **kwargs):
        req = self.get_object()
        apps = Appliccation.objects.filter(request=req)
        us = User.objects.all()

        for u in us:
            for a in apps:
                if u == a.repairman:
                    notif = '<div class="col-sm-2 col-md-2 col-lg-2 align-items-center justify-content" style="margin: auto">'
                    notif += f'<a href="{ reverse("info", kwargs={"pk": req.user.id}) }">'
                    notif += f'<img class="rounded-circle navbar-img" src="{ req.user.profile.photo.url }">'
                    notif += '</a></div>' + f'<div class="col-sm-7 col-md-7 col-lg-7"><a href="{ reverse("info", kwargs={"pk": req.user.id}) }">' + req.user.username + '</a>' + f' deleted posted job (<a href="{ reverse("request_detail", kwargs={"pk": req.id}) }"> { req.job_title } </a>) for which you\'ve applied for!'
                    notif += f'<a href="{ reverse("messages", kwargs={"username": req.user}) }"><i class="messagge nav-item nav-link fas fa-envelope mt-1" style="color: red"></i></a></div>'
                    url = f'{ reverse("info", kwargs={"pk": req.user.id}) }'
                    rep_not = RepairmanNotifications(repairman=u, notification=notif, url_to_go=url)
                    rep_not.save()

        messages.success(request, f'You\'ve deleted posted request successfuly!')
        return super(RequestDeleteView, self).delete(request, *args, **kwargs)


@login_required
def search(request):
    q = request.GET.get('q')
    users = User.objects.all()
    prof = ''
    name = ''
    if q:
        prof = Profile.objects.filter(Q(profession__contains=q))
        name = User.objects.filter(Q(first_name__contains=q) | Q(last_name__contains=q))

    f = 0
    if prof or name:
        f = 1

    # prof = User.objects.filter(Q(first_name__contains=q) | Q(last_name__contains=q))

    """
    us = User.objects.filter(id=selfrequest.user)
    hired = Hire.objects.filter(user=us)

    f_hired = []
    for u in users:
        for h in hired:
            if h.user == us and h.repairman == u.id and h.status == 'pending':
                f_hired.append(u)
    """

    us = request.user

    hired = Hire.objects.filter(user=us)

    f_hired = []
    for u in users:
        for h in hired:
            if h.user == us and h.repairman == u.id and h.status == 'pending':
                f_hired.append(u)

    not_c = ClientNotifications.objects.filter(client=us, remove=False).order_by('-date')
    not_cli = ClientNotifications.objects.filter(client=us, seen=False).count()
    mess_cli = ClientMessage.objects.filter((Q(client=us) | Q(sender=us)) & Q(seen=False)).order_by("-date")
    mess_cli_c = ClientMessage.objects.filter(Q(client=us) & Q(seen_notif=False)).count()

    origin = us.profile.address
    distance = {}
    for u in users:
        if u.profile.role == 'repairman':
            dist = '-'
            api = urllib.request.urlopen(f'https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins={ urllib.parse.quote(origin) }&destinations={ urllib.parse.quote(u.profile.address) }&key={ api_key }').read(1000)
            data = json.loads(api.decode('utf-8'))
            if data['rows'][0]['elements'][0]['status'] == 'OK':
                dist = data['rows'][0]['elements'][0]['distance']['text']

            distance.update({u.id: dist})

    context = {
        'not_c': not_c,
        'not_cli': not_cli,
        'mess_cli': mess_cli,
        'mess_cli_c': mess_cli_c,
        'users': users,
        'f_hired': f_hired,
        'q': q,
        'f': f,
        'prof': prof,
        'name': name,
        'dist': distance
    }

    # context.update(csrf(request))

    return render(request, 'need_a_help_app/search_results.html', context)


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

    # ako zaposlim majstora povecavam broj zaposlenja
    us.profile.num_hires += 1
    us.save()
    rep.profile.hired += 1
    rep.save()

    notif = f'<div class="col-sm-2 col-md-2 col-lg-2 align-items-center justify-content" style="margin: auto"><a href="{ reverse("info", kwargs={"pk": us.id}) }">' + f'<img class="rounded-circle navbar-img" src="{ us.profile.photo.url }">'
    notif += '</a></div>' + f'<div class="col-sm-7 col-md-7 col-lg-7"><a href="{ reverse("info", kwargs={"pk": us.id}) }">' + us.username + '</a> hired you for a job!'
    notif += f'<a href="{ reverse("messages", kwargs={"username": us}) }"><i class="messagge nav-item nav-link fas fa-envelope mt-1" style="color: red"></i></a></div>'
    url = f'{ reverse("requests_repairman", kwargs={"pk": rep_id}) }'
    rep_not = RepairmanNotifications(repairman=rep, notification=notif, url_to_go=url)
    rep_not.save()

    messages.success(request, f'You\'ve hired repairman successfuly! Wait him to accept!')
    return redirect('info', pk=rep_id)


class HiredListView(LoginRequiredMixin, ListView):
    model = Hire
    template_name = 'need_a_help_app/hired_user.html'
    context_object_name = 'hir'
    paginate_by = 2

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs.get('pk'))
        return Hire.objects.filter(user=user, done=False).order_by('-date')

    def get_context_data(self, **kwargs):
        context_data = super(HiredListView, self).get_context_data(**kwargs)

        users = User.objects.all()
        job = JobHire.objects.filter(done=False).order_by('-date_hired')

        get_not_c = self.request.GET.get('not_c', -1)

        if get_not_c != -1:
            not_seen = ClientNotifications.objects.filter(id=get_not_c).first()
            not_seen.seen = True
            not_seen.save()

        us = self.request.user
        not_c = ClientNotifications.objects.filter(client=us, remove=False).order_by('-date')
        not_cli = ClientNotifications.objects.filter(client=us, seen=False).count()
        mess_cli = ClientMessage.objects.filter((Q(client=us) | Q(sender=us)) & Q(seen=False)).order_by("-date")
        mess_cli_c = ClientMessage.objects.filter(Q(client=us) & Q(seen_notif=False)).count()
        done_job = Hire.objects.filter(user=us, status='done', accepted=True, done=False).count()
        done_req = JobHire.objects.filter(status='done', done=False).count()

        context_data['us'] = users
        context_data['job'] = job
        context_data['not_c'] = not_c
        context_data['not_cli'] = not_cli
        context_data['done_job'] = done_job
        context_data['done_req'] = done_req
        context_data['mess_cli'] = mess_cli
        context_data['mess_cli_c'] = mess_cli_c

        return context_data


class HiredReqListView(LoginRequiredMixin, ListView):
    model = JobHire
    template_name = 'need_a_help_app/hired_req_user.html'
    context_object_name = 'job'
    paginate_by = 2

    def get_queryset(self):
        return JobHire.objects.filter(done=False).order_by('-date_hired')

    def get_context_data(self, **kwargs):
        context_data = super(HiredReqListView, self).get_context_data(**kwargs)

        get_not_c = self.request.GET.get('not_c', -1)

        if get_not_c != -1:
            not_seen = ClientNotifications.objects.filter(id=get_not_c).first()
            not_seen.seen = True
            not_seen.save()

        us = self.request.user
        not_c = ClientNotifications.objects.filter(client=us, remove=False).order_by('-date')
        not_cli = ClientNotifications.objects.filter(client=us, seen=False).count()
        done_job = Hire.objects.filter(user=us, status='done', accepted=True, done=False).count()
        done_req = JobHire.objects.filter(status='done', done=False).count()
        mess_cli = ClientMessage.objects.filter((Q(client=us) | Q(sender=us)) & Q(seen=False)).order_by("-date")
        mess_cli_c = ClientMessage.objects.filter(Q(client=us) & Q(seen_notif=False)).count()

        context_data['not_c'] = not_c
        context_data['not_cli'] = not_cli
        context_data['done_job'] = done_job
        context_data['done_req'] = done_req
        context_data['mess_cli'] = mess_cli
        context_data['mess_cli_c'] = mess_cli_c

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

        get_not = self.request.GET.get('not', -1)

        if get_not != -1:
            not_seen = RepairmanNotifications.objects.filter(id=get_not).first()
            not_seen.seen = True
            not_seen.save()

        users = User.objects.all()
        us = self.request.user
        req = RepairmanRequests.objects.filter(repairman=us, seen=False).count()
        act_job = RepairmanRequests.objects.filter(repairman=us, active=True, done=False).count()
        act_req = JobHire.objects.filter(repairman=us, status='pending').count()
        act_cnt = act_job + act_req
        not_r = RepairmanNotifications.objects.filter(repairman=us, remove=False).order_by('-date')
        not_rep = RepairmanNotifications.objects.filter(repairman=us, seen=False).count()
        mess_cli = ClientMessage.objects.filter((Q(client=us) | Q(sender=us)) & Q(seen=False)).order_by("-date")
        mess_cli_c = ClientMessage.objects.filter(Q(client=us) & Q(seen_notif=False)).count()

        context_data['us'] = users
        context_data['cnt'] = req
        self.request.session['cnt'] = req
        context_data['act_cnt'] = act_cnt
        context_data['not_r'] = not_r
        context_data['not_rep'] = not_rep
        context_data['mess_cli'] = mess_cli
        context_data['mess_cli_c'] = mess_cli_c

        return context_data


@login_required
def job_accept(request, user_id, rep_id):
    users = User.objects.all()
    rep = User.objects.filter(id=rep_id).first()
    rep_req = RepairmanRequests.objects.filter(user=user_id, repairman=rep).order_by('-date')

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

    notif = f'<div class="col-sm-2 col-md-2 col-lg-2 align-items-center justify-content" style="margin: auto"><a href="{ reverse("info", kwargs={"pk": rep.id}) }">' + f'<img class="rounded-circle navbar-img" src="{ rep.profile.photo.url }">'
    notif += '</a></div>' + f'<div class="col-sm-7 col-md-7 col-lg-7"><a href="{ reverse("info", kwargs={"pk": rep.id}) }">' + rep.username + '</a> accepted a job you\'ve hired him for!'
    notif += f'<a href="{ reverse("messages", kwargs={"username": rep}) }"><i class="messagge nav-item nav-link fas fa-envelope mt-1" style="color: red"></i></a></div>'
    url = f'{ reverse("hired_user", kwargs={"pk": us.id}) }'
    cli_not = ClientNotifications(client=us, notification=notif, url_to_go=url)
    cli_not.save()

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

        get_not = self.request.GET.get('not', -1)

        if get_not != -1:
            not_seen = RepairmanNotifications.objects.filter(id=get_not).first()
            not_seen.seen = True
            not_seen.save()

        cnt = RepairmanRequests.objects.filter(repairman=us, seen=False).count()
        act_job = RepairmanRequests.objects.filter(repairman=us, active=True, done=False).count()
        act_req = JobHire.objects.filter(repairman=us, status='pending').count()
        act_cnt = act_job + act_req
        not_r = RepairmanNotifications.objects.filter(repairman=us, remove=False).order_by('-date')
        not_rep = RepairmanNotifications.objects.filter(repairman=us, seen=False).count()
        mess_cli = ClientMessage.objects.filter((Q(client=us) | Q(sender=us)) & Q(seen=False)).order_by("-date")
        mess_cli_c = ClientMessage.objects.filter(Q(client=us) & Q(seen_notif=False)).count()

        req = Requests.objects.filter(visible=False)

        origin = us.profile.address
        distance = {}
        for r in req:
            dist = '-'
            api = urllib.request.urlopen(f'https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins={ urllib.parse.quote(origin) }&destinations={ urllib.parse.quote(r.address) }&key={ api_key }').read(1000)
            data = json.loads(api.decode('utf-8'))
            if data['rows'][0]['elements'][0]['status'] == 'OK':
                dist = data['rows'][0]['elements'][0]['distance']['text']

            distance.update({r.id: dist})

        context_data['us'] = users
        context_data['job'] = job
        context_data['cnt'] = cnt
        context_data['act_job'] = act_job
        context_data['act_req'] = act_req
        context_data['act_cnt'] = act_cnt
        context_data['not_r'] = not_r
        context_data['not_rep'] = not_rep
        context_data['dist'] = distance
        context_data['mess_cli'] = mess_cli
        context_data['mess_cli_c'] = mess_cli_c

        return context_data


class RepairmanActiveReqListView(LoginRequiredMixin, ListView):
    model = JobHire
    template_name = 'need_a_help_app/active_req_repairman.html'
    context_object_name = 'job'
    paginate_by = 2

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs.get('pk'))
        return JobHire.objects.filter(repairman=user, status='pending').order_by('-date_hired')

    def get_context_data(self, **kwargs):
        context_data = super(RepairmanActiveReqListView, self).get_context_data(**kwargs)

        us = self.request.user

        get_not = self.request.GET.get('not', -1)

        if get_not != -1:
            not_seen = RepairmanNotifications.objects.filter(id=get_not).first()
            not_seen.seen = True
            not_seen.save()

        cnt = RepairmanRequests.objects.filter(repairman=us, seen=False).count()
        act_job = RepairmanRequests.objects.filter(repairman=us, active=True, done=False).count()
        act_req = JobHire.objects.filter(repairman=us, status='pending').count()
        act_cnt = act_job + act_req
        not_r = RepairmanNotifications.objects.filter(repairman=us, remove=False).order_by('-date')
        not_rep = RepairmanNotifications.objects.filter(repairman=us, seen=False).count()
        mess_cli = ClientMessage.objects.filter((Q(client=us) | Q(sender=us)) & Q(seen=False)).order_by("-date")
        mess_cli_c = ClientMessage.objects.filter(Q(client=us) & Q(seen_notif=False)).count()

        req = Requests.objects.filter(visible=False)

        origin = us.profile.address
        distance = {}
        for r in req:
            dist = '-'
            api = urllib.request.urlopen(f'https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins={ urllib.parse.quote(origin) }&destinations={ urllib.parse.quote(r.address) }&key={ api_key }').read(1000)
            data = json.loads(api.decode('utf-8'))
            if data['rows'][0]['elements'][0]['status'] == 'OK':
                dist = data['rows'][0]['elements'][0]['distance']['text']

            distance.update({r.id: dist})

        context_data['cnt'] = cnt
        context_data['act_job'] = act_job
        context_data['act_req'] = act_req
        context_data['act_cnt'] = act_cnt
        context_data['not_r'] = not_r
        context_data['not_rep'] = not_rep
        context_data['dist'] = distance
        context_data['mess_cli'] = mess_cli
        context_data['mess_cli_c'] = mess_cli_c

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

    rep = User.objects.filter(id=rep_id).first()

    notif = f'<div class="col-sm-2 col-md-2 col-lg-2 align-items-center justify-content" style="margin: auto"><a href="{ reverse("info", kwargs={"pk": rep.id}) }">' + f'<img class="rounded-circle navbar-img" src="{ rep.profile.photo.url }">'
    notif += '</a></div>' + f'<div class="col-sm-7 col-md-7 col-lg-7"><a href="{ reverse("info", kwargs={"pk": rep.id}) }">' + rep.username + '</a> finished a job you\'ve hired him for!'
    notif += f'<a href="{ reverse("messages", kwargs={"username": rep}) }"><i class="messagge nav-item nav-link fas fa-envelope mt-1" style="color: red"></i></a></div>'
    url = f'{ reverse("hired_user", kwargs={"pk": us.id}) }'
    cli_not = ClientNotifications(client=us, notification=notif, url_to_go=url)
    cli_not.save()

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
        cnt = RepairmanRequests.objects.filter(repairman=us, seen=False).count()
        act_job = RepairmanRequests.objects.filter(repairman=us, active=True, done=False).count()
        act_req = JobHire.objects.filter(repairman=us, status='pending').count()
        act_cnt = act_job + act_req
        not_r = RepairmanNotifications.objects.filter(repairman=us, remove=False).order_by('-date')
        not_rep = RepairmanNotifications.objects.filter(repairman=us, seen=False).count()
        mess_cli = ClientMessage.objects.filter((Q(client=us) | Q(sender=us)) & Q(seen=False)).order_by("-date")
        mess_cli_c = ClientMessage.objects.filter(Q(client=us) & Q(seen_notif=False)).count()

        req = Requests.objects.filter(visible=False)

        origin = us.profile.address
        distance = {}
        for r in req:
            dist = '-'
            api = urllib.request.urlopen(f'https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins={ urllib.parse.quote(origin) }&destinations={ urllib.parse.quote(r.address) }&key={ api_key }').read(1000)
            data = json.loads(api.decode('utf-8'))
            if data['rows'][0]['elements'][0]['status'] == 'OK':
                dist = data['rows'][0]['elements'][0]['distance']['text']

            distance.update({r.id: dist})

        context_data['us'] = users
        context_data['done'] = job_done
        context_data['cnt'] = cnt
        context_data['act_cnt'] = act_cnt
        context_data['not_r'] = not_r
        context_data['not_rep'] = not_rep
        context_data['dist'] = distance
        context_data['mess_cli'] = mess_cli
        context_data['mess_cli_c'] = mess_cli_c

        return context_data


class RepairmanDoneReqListView(LoginRequiredMixin, ListView):
    model = JobHire
    template_name = 'need_a_help_app/done_req_repairman.html'
    context_object_name = 'done'
    paginate_by = 2

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs.get('pk'))
        return JobHire.objects.filter(repairman=user, status='done').order_by('-date_hired')

    def get_context_data(self, **kwargs):
        context_data = super(RepairmanDoneReqListView, self).get_context_data(**kwargs)

        us = self.request.user
        cnt = RepairmanRequests.objects.filter(repairman=us, seen=False).count()
        act_job = RepairmanRequests.objects.filter(repairman=us, active=True, done=False).count()
        act_req = JobHire.objects.filter(repairman=us, status='pending').count()
        act_cnt = act_job + act_req
        not_r = RepairmanNotifications.objects.filter(repairman=us, remove=False).order_by('-date')
        not_rep = RepairmanNotifications.objects.filter(repairman=us, seen=False).count()
        mess_cli = ClientMessage.objects.filter((Q(client=us) | Q(sender=us)) & Q(seen=False)).order_by("-date")
        mess_cli_c = ClientMessage.objects.filter(Q(client=us) & Q(seen_notif=False)).count()

        req = Requests.objects.filter(visible=False)

        origin = us.profile.address
        distance = {}
        for r in req:
            dist = '-'
            api = urllib.request.urlopen(f'https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins={ urllib.parse.quote(origin) }&destinations={ urllib.parse.quote(r.address) }&key={ api_key }').read(1000)
            data = json.loads(api.decode('utf-8'))
            if data['rows'][0]['elements'][0]['status'] == 'OK':
                dist = data['rows'][0]['elements'][0]['distance']['text']

            distance.update({r.id: dist})

        context_data['cnt'] = cnt
        context_data['act_cnt'] = act_cnt
        context_data['not_r'] = not_r
        context_data['not_rep'] = not_rep
        context_data['dist'] = distance
        context_data['mess_cli'] = mess_cli
        context_data['mess_cli_c'] = mess_cli_c

        return context_data


@login_required
def repairman_apply(request, us_id, req_id):
    us = User.objects.filter(id=us_id).first()
    req = Requests.objects.filter(id=req_id).first()
    app = Appliccation.objects.filter(repairman=us, request=req)

    if not app:
        app_save = Appliccation(repairman=us, request=req)
        app_save.save()

        notif = f'<div class="col-sm-2 col-md-2 col-lg-2 align-items-center justify-content" style="margin: auto"><a href="{ reverse("info", kwargs={"pk": us.id}) }">' + f'<img class="rounded-circle navbar-img" src="{ us.profile.photo.url }">'
        notif += '</a></div>' + f'<div class="col-sm-7 col-md-7 col-lg-7"><a href="{ reverse("info", kwargs={"pk": us.id}) }">' + us.username + f'</a> applied for a job <i>{ req.job_title }</i>!'
        notif += f'<a href="{ reverse("messages", kwargs={"username": us}) }"><i class="messagge nav-item nav-link fas fa-envelope mt-1" style="color: red"></i></a></div>'
        url = f'{ reverse("request_detail", kwargs={"pk": req.id}) }'
        cli_not = ClientNotifications(client=req.user, notification=notif, url_to_go=url)
        cli_not.save()

        messages.success(request, f'You\'ve successfuly applied for a job { req.job_title }!')
        return redirect('request_detail', pk=req.id)
    else:
        messages.warning(request, f'You\'ve already applied for a job { req.job_title }!')
        return redirect('request_detail', pk=req.id)


class RepairmanApplicationsListView(LoginRequiredMixin, ListView):
    model = Appliccation
    template_name = 'need_a_help_app/repairman_apps.html'
    context_object_name = 'req'
    paginate_by = 4

    def get_queryset(self):
        return Requests.objects.filter(visible=True).order_by('-date')

    def get_context_data(self, **kwargs):
        context_data = super(RepairmanApplicationsListView, self).get_context_data(**kwargs)

        us = self.request.user
        cnt = RepairmanRequests.objects.filter(repairman=us, seen=False).count()
        act_job = RepairmanRequests.objects.filter(repairman=us, active=True, done=False).count()
        act_req = JobHire.objects.filter(repairman=us, status='pending').count()
        act_cnt = act_job + act_req
        not_r = RepairmanNotifications.objects.filter(repairman=us, remove=False).order_by('-date')
        not_rep = RepairmanNotifications.objects.filter(repairman=us, seen=False).count()
        mess_cli = ClientMessage.objects.filter((Q(client=us) | Q(sender=us)) & Q(seen=False)).order_by("-date")
        mess_cli_c = ClientMessage.objects.filter(Q(client=us) & Q(seen_notif=False)).count()
        app = Appliccation.objects.filter(repairman=us)

        req = Requests.objects.filter(visible=True)

        origin = us.profile.address
        distance = {}
        for r in req:
            dist = '-'
            api = urllib.request.urlopen(f'https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins={ urllib.parse.quote(origin) }&destinations={ urllib.parse.quote(r.address) }&key={ api_key }').read(1000)
            data = json.loads(api.decode('utf-8'))
            if data['rows'][0]['elements'][0]['status'] == 'OK':
                dist = data['rows'][0]['elements'][0]['distance']['text']

            distance.update({r.id: dist})

        context_data['cnt'] = cnt
        context_data['not_r'] = not_r
        context_data['not_rep'] = not_rep
        context_data['act_cnt'] = act_cnt
        context_data['app'] = app
        context_data['dist'] = distance
        context_data['mess_cli'] = mess_cli
        context_data['mess_cli_c'] = mess_cli_c

        return context_data


@login_required
def posted_job_hire(request, us_id, req_id):
    us = User.objects.filter(id=us_id).first()
    req = Requests.objects.filter(id=req_id).first()
    job = JobHire.objects.filter(repairman=us, request=req)

    req.visible = False
    req.save()

    # ako zaposlim majstora povecavam broj zaposlenja
    logged = request.user
    us.profile.hired += 1
    us.save()
    logged.profile.num_hires += 1
    logged.save()

    if not job:
        job_save = JobHire(repairman=us, request=req)
        job_save.save()

        notif = f'<div class="col-sm-2 col-md-2 col-lg-2 align-items-center justify-content" style="margin: auto"><a href="{ reverse("info", kwargs={"pk": req.user.id}) }">' + f'<img class="rounded-circle navbar-img" src="{ req.user.profile.photo.url }">'
        notif += '</a></div>' + f'<div class="col-sm-7 col-md-7 col-lg-7"><a href="{ reverse("info", kwargs={"pk": req.user.id}) }">' + req.user.username + '</a>' + f' hired you for a job <a href="{ reverse("request_detail", kwargs={"pk": req.id}) }">{ req.job_title }</a>!'
        notif += f'<a href="{ reverse("messages", kwargs={"username": req.user}) }"><i class="messagge nav-item nav-link fas fa-envelope mt-1" style="color: red"></i></a></div>'
        url = f'{ reverse("active_req_repairman", kwargs={"pk": us.id}) }'
        rep_not = RepairmanNotifications(repairman=us, notification=notif, url_to_go=url)
        rep_not.save()

        messages.success(request, f'You\'ve hired { us.username } for a job { req.job_title }!')
        return redirect('hired_req_user', pk=req.user.id)


@login_required
def posted_job_done(request, us_id, req_id):
    us = User.objects.filter(id=us_id).first()
    req = Requests.objects.filter(id=req_id).first()
    job = JobHire.objects.filter(repairman=us, request=req).first()

    job.status = 'done'
    job.save()

    notif = f'<div class="col-sm-2 col-md-2 col-lg-2 align-items-center justify-content" style="margin: auto"><a href="{ reverse("info", kwargs={"pk": us.id}) }">' + f'<img class="rounded-circle navbar-img" src="{ us.profile.photo.url }">'
    notif += '</a></div>' + f'<div class="col-sm-7 col-md-7 col-lg-7"><a href="{ reverse("info", kwargs={"pk": us.id}) }">' + us.username + '</a>' + f' finished the job <a href="{ reverse("request_detail", kwargs={"pk": req.id}) }">{ req.job_title }</a> you\'ve hired him for!'
    notif += f'<a href="{ reverse("messages", kwargs={"username": us}) }"><i class="messagge nav-item nav-link fas fa-envelope mt-1" style="color: red"></i></a></div>'
    url = f'{ reverse("hired_req_user", kwargs={"pk": req.user.id}) }'
    cli_not = ClientNotifications(client=req.user, notification=notif, url_to_go=url)
    cli_not.save()

    messages.success(request, f'You\'ve finished a job { req.job_title } for { req.user.username }!')
    return redirect('done_req_repairman', pk=us.id)


class JobHireDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Requests

    def test_func(self):
        req = self.get_object()
        if self.request.user == req.user:
            return True
        return False

    def get_success_url(self):
        user = self.object.user
        return reverse_lazy('hired_user', kwargs={'pk': user.id})

    def delete(self, request, *args, **kwargs):
        req = self.get_object()
        hir = JobHire.objects.filter(request=req).first()
        rep = hir.repairman
        us = self.object.user

        # ako klijent otkaže posao brisu se zaposlenja majstora i klijenta, ne smije ispod nule
        if us.profile.num_hires > 0:
            us.profile.num_hires -= 1
            us.save()
        if rep.profile.hired > 0:
            rep.profile.hired -= 1
            rep.save()

        notif = f'<div class="col-sm-2 col-md-2 col-lg-2 align-items-center justify-content" style="margin: auto"><a href="{ reverse("info", kwargs={"pk": us.id}) }">' + f'<img class="rounded-circle navbar-img" src="{ us.profile.photo.url }">'
        notif += '</a></div>' + f'<div class="col-sm-7 col-md-7 col-lg-7"><a href="{ reverse("info", kwargs={"pk": us.id}) }">' + us.username + '</a>' + f' canceled/deleted the posted job ( { req.job_title } ) for which you were hired!'
        notif += f'<a href="{ reverse("messages", kwargs={"username": us}) }"><i class="messagge nav-item nav-link fas fa-envelope mt-1" style="color: red"></i></a></div>'
        url = f'{ reverse("info", kwargs={"pk": us.id}) }'
        rep_not = RepairmanNotifications(repairman=rep, notification=notif, url_to_go=url)
        rep_not.save()

        messages.success(request, f'You\'ve deleted posted request where you hired a repairman successfuly!')
        return super(JobHireDeleteView, self).delete(request, *args, **kwargs)


@login_required
def cancel_application(request, user_id, req_id):
    us = User.objects.filter(id=user_id).first()
    req = Requests.objects.filter(id=req_id).first()
    Appliccation.objects.filter(repairman=us, request=req).delete()

    messages.success(request, f'You\'ve quit the job { req.job_title } that you have been applied for!')
    return redirect('repairman_apps', pk=us.id)


@login_required
def client_repairman_job_delete(request, user_id, rep_id, log_id, txt):
    us = User.objects.filter(id=user_id).first()
    hir = Hire.objects.filter(user=us, repairman=rep_id)

    h_to_del = hir
    for h in hir:
        if h.status == 'pending':
            h_to_del = h
            break

    h_to_del.delete()

    rep = User.objects.filter(id=rep_id).first()
    req = RepairmanRequests.objects.filter(repairman=rep, user=user_id)

    log = User.objects.filter(id=log_id).first()

    r_to_del = req
    for r in req:
        if r.done is False:
            r_to_del = r
            break

    r_to_del.delete()

    # ako klijent otkaže posao brisu se zaposlenja majstora i klijenta, ne smije ispod nule
    if us.profile.num_hires > 0:
        us.profile.num_hires -= 1
        us.save()
    if rep.profile.hired > 0:
        rep.profile.hired -= 1
        rep.save()

    if log.profile.role == 'client':
        notif = f'<div class="col-sm-2 col-md-2 col-lg-2 align-items-center justify-content" style="margin: auto"><a href="{ reverse("info", kwargs={"pk": us.id}) }">' + f'<img class="rounded-circle navbar-img" src="{ us.profile.photo.url }">'
        notif += '</a></div>' + f'<div class="col-sm-7 col-md-7 col-lg-7"><a href="{ reverse("info", kwargs={"pk": us.id}) }">' + us.username + '</a> canceled the job for which you were hired!'
        notif += f'<a href="{ reverse("messages", kwargs={"username": us}) }"><i class="messagge nav-item nav-link fas fa-envelope mt-1" style="color: red"></i></a></div>'
        url = f'{ reverse("info", kwargs={"pk": us.id}) }'
        rep_not = RepairmanNotifications(repairman=rep, notification=notif, url_to_go=url)
        rep_not.save()

        messages.success(request, f'You\'ve canceled the job for which you hired { rep.username }!')
        return redirect('hired_user', pk=log.id)
    else:
        notif = f'<div class="col-sm-2 col-md-2 col-lg-2 align-items-center justify-content" style="margin: auto"><a href="{ reverse("info", kwargs={"pk": rep.id}) }">' + f'<img class="rounded-circle navbar-img" src="{ rep.profile.photo.url }">'
        notif += '</a></div>' + f'<div class="col-sm-7 col-md-7 col-lg-7"><a href="{ reverse("info", kwargs={"pk": rep.id}) }">' + rep.username + '</a> quit the job you\'ve hired him!'
        notif += f'<a href="{ reverse("messages", kwargs={"username": rep}) }"><i class="messagge nav-item nav-link fas fa-envelope mt-1" style="color: red"></i></a></div>'
        url = f'{ reverse("info", kwargs={"pk": rep.id}) }'
        cli_not = ClientNotifications(client=us, notification=notif, url_to_go=url)
        cli_not.save()

        messages.success(request, f'You quit the job for which you were hired by { us.username }!')
        if txt == 'req':
            return redirect('requests_repairman', pk=rep_id)
        elif txt == 'act':
            return redirect('active_repairman', pk=rep_id)


class NotificationsClientListView(LoginRequiredMixin, ListView):
    model = ClientNotifications
    template_name = 'need_a_help_app/notifications_client.html'
    context_object_name = 'notif'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs.get('pk'))
        return ClientNotifications.objects.filter(client=user).order_by('-date')

    def get_context_data(self, **kwargs):
        context_data = super(NotificationsClientListView, self).get_context_data(**kwargs)

        users = User.objects.all()
        us = self.request.user
        not_c = ClientNotifications.objects.filter(client=us, remove=False).order_by('-date')
        not_cli = ClientNotifications.objects.filter(client=us, seen=False).count()
        mess_cli = ClientMessage.objects.filter((Q(client=us) | Q(sender=us)) & Q(seen=False)).order_by("-date")
        mess_cli_c = ClientMessage.objects.filter(Q(client=us) & Q(seen_notif=False)).count()

        context_data['us'] = users
        context_data['not_c'] = not_c
        context_data['not_cli'] = not_cli
        context_data['mess_cli'] = mess_cli
        context_data['mess_cli_c'] = mess_cli_c


        return context_data


class NotificationsRepairmanListView(LoginRequiredMixin, ListView):
    model = RepairmanNotifications
    template_name = 'need_a_help_app/notifications_repairman.html'
    context_object_name = 'notif'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs.get('pk'))
        return RepairmanNotifications.objects.filter(repairman=user).order_by('-date')

    def get_context_data(self, **kwargs):
        context_data = super(NotificationsRepairmanListView, self).get_context_data(**kwargs)

        users = User.objects.all()
        us = self.request.user
        not_r = RepairmanNotifications.objects.filter(repairman=us, remove=False).order_by('-date')
        not_rep = RepairmanNotifications.objects.filter(repairman=us, seen=False).count()
        mess_cli = ClientMessage.objects.filter((Q(client=us) | Q(sender=us)) & Q(seen=False)).order_by("-date")
        mess_cli_c = ClientMessage.objects.filter(Q(client=us) & Q(seen_notif=False)).count()

        context_data['us'] = users
        context_data['not_r'] = not_r
        context_data['not_rep'] = not_rep
        context_data['mess_cli'] = mess_cli
        context_data['mess_cli_c'] = mess_cli_c

        return context_data


@login_required
def rate(request):
    if request.method == 'GET':
        val = request.GET['val']
        feed = request.GET['feedback']
        id_r = request.GET.get('rep_id')
        req = request.GET.get('req')  # ako je jedan radi se o ratingu requesta inače o ratingu posla u struci
        job = request.GET.get('job')

    us = request.user
    rep = User.objects.filter(id=id_r).first()

    if val == '0' and job == '1':
        messages.warning(request, f'You did not finished rating { rep.first_name }, do it again to move it to done list!')
        return redirect('hired_user', pk=us.id)

    if val == '0' and req == '1':
        messages.warning(request, f'You did not finished rating { rep.first_name }, do it again to move it to done list!')
        return redirect('hired_req_user', pk=us.id)

    rate = Rate(repairman=rep, user=us, rate=val, feedback=feed)
    rate.save()

    # povecava se broj rateova za majstora
    rep.profile.rated += 1
    rep.save()

    if job == '1':
        jobs = Hire.objects.filter(user=us, repairman=rep.id, status='done', done=False).order_by('-date').first()
        jobs.done = True
        jobs.save()
    elif req == '1':
        reqs = JobHire.objects.filter(repairman=rep, status='done', done=False).order_by('-date_hired').first()
        reqs.done = True
        reqs.save()

    rat = Rate.objects.all()

    sum_r = 0.0
    cnt = 0.0
    for r in rat:
        if r.repairman == rep:
            cnt += 1.0
            sum_r += r.rate

    total = sum_r / cnt
    total = round(total, 1)

    rate_save = Profile.objects.filter(user=rep).first()
    rate_save.rating = total
    rate_save.save()

    notif = '<div class="col-sm-2 col-md-2 col-lg-2 align-items-center justify-content" style="margin: auto">'
    notif += f'<a href="{ reverse("info", kwargs={"pk": us.id}) }">'
    notif += f'<img class="rounded-circle navbar-img" src="{ us.profile.photo.url }">'
    notif += '</a></div>' + f'<div class="col-sm-7 col-md-7 col-lg-7"><a href="{ reverse("info", kwargs={"pk": us.id}) }">' + us.username + '</a>' + f' rated you with { val } stars, check your profile to see more details!'
    notif += f'<a href="{ reverse("messages", kwargs={"username": us}) }"><i class="messagge nav-item nav-link fas fa-envelope mt-1" style="color: red"></i></a></div>'
    url = f'{ reverse("info", kwargs={"pk": rep.id}) }'
    rep_not = RepairmanNotifications(repairman=rep, notification=notif, url_to_go=url)
    rep_not.save()

    messages.success(request, f'You\'ve successfully rated repairman { rep.username }!')
    if job == '1':
        return redirect('done_user', pk=us.id)
    elif req == '1':
        return redirect('done_req_user', pk=us.id)


class UserDoneListView(LoginRequiredMixin, ListView):
    model = Hire
    template_name = 'need_a_help_app/done_user.html'
    context_object_name = 'hir'
    paginate_by = 4

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs.get('pk'))
        return Hire.objects.filter(user=user, done=True).order_by('-date')

    def get_context_data(self, **kwargs):
        context_data = super(UserDoneListView, self).get_context_data(**kwargs)

        users = User.objects.all()
        job = JobHire.objects.filter(done=True).order_by('-date_hired')

        us = self.request.user
        not_c = ClientNotifications.objects.filter(client=us, remove=False).order_by('-date')
        not_cli = ClientNotifications.objects.filter(client=us, seen=False).count()
        mess_cli = ClientMessage.objects.filter((Q(client=us) | Q(sender=us)) & Q(seen=False)).order_by("-date")
        mess_cli_c = ClientMessage.objects.filter(Q(client=us) & Q(seen_notif=False)).count()
        done_job = Hire.objects.filter(user=us, status='done', accepted=True, done=True).count()
        done_req = JobHire.objects.filter(status='done', done=True).count()

        context_data['us'] = users
        context_data['job'] = job
        context_data['not_c'] = not_c
        context_data['not_cli'] = not_cli
        context_data['mess_cli'] = mess_cli
        context_data['mess_cli_c'] = mess_cli_c
        context_data['done_job'] = done_job
        context_data['done_req'] = done_req
        context_data['us_list'] = list(User.objects.all())

        return context_data


class UserDoneReqListView(LoginRequiredMixin, ListView):
    model = JobHire
    template_name = 'need_a_help_app/done_req_user.html'
    context_object_name = 'job'
    paginate_by = 4

    def get_queryset(self):
        return JobHire.objects.filter(done=True).order_by('-date_hired')

    def get_context_data(self, **kwargs):
        context_data = super(UserDoneReqListView, self).get_context_data(**kwargs)

        us = self.request.user
        not_c = ClientNotifications.objects.filter(client=us, remove=False).order_by('-date')
        not_cli = ClientNotifications.objects.filter(client=us, seen=False).count()
        done_job = Hire.objects.filter(user=us, status='done', accepted=True, done=True).count()
        done_req = JobHire.objects.filter(status='done', done=True).count()
        mess_cli = ClientMessage.objects.filter((Q(client=us) | Q(sender=us)) & Q(seen=False)).order_by("-date")
        mess_cli_c = ClientMessage.objects.filter(Q(client=us) & Q(seen_notif=False)).count()

        context_data['not_c'] = not_c
        context_data['not_cli'] = not_cli
        context_data['done_job'] = done_job
        context_data['done_req'] = done_req
        context_data['mess_cli'] = mess_cli
        context_data['mess_cli_c'] = mess_cli_c

        return context_data


class TopRatedView(LoginRequiredMixin, ListView):
    template_name = 'need_a_help_app/top_rated.html'
    context_object_name = 'filter'
    paginate_by = 5

    def get_queryset(self):
        qs = Profile.objects.filter(role='repairman').order_by('-rating')
        return TopRatedFilter(self.request.GET, queryset=qs).qs

    def get_context_data(self, **kwargs):
        context_data = super(TopRatedView, self).get_context_data(**kwargs)

        us = self.request.user
        reqq_seen = SeenRequest.objects.filter(user=us)

        hired = Hire.objects.filter(user=us)
        uss = User.objects.all()

        f_hired = []
        for u in uss:
            for h in hired:
                if h.user == us and h.repairman == u.id and h.status == 'pending':
                    f_hired.append(u)

        get_not = self.request.GET.get('not', -1)
        get_not_c = self.request.GET.get('not_c', -1)

        if get_not != -1:
            not_seen = RepairmanNotifications.objects.filter(id=get_not).first()
            not_seen.seen = True
            not_seen.save()

        if get_not_c != -1:
            not_seen = ClientNotifications.objects.filter(id=get_not_c).first()
            not_seen.seen = True
            not_seen.save()

        cnt = RepairmanRequests.objects.filter(repairman=us, seen=False).count()
        act_job = RepairmanRequests.objects.filter(repairman=us, active=True, done=False).count()
        act_req = JobHire.objects.filter(repairman=us, status='pending').count()
        act_cnt = act_job + act_req
        not_r = RepairmanNotifications.objects.filter(repairman=us, remove=False).order_by('-date')
        not_c = ClientNotifications.objects.filter(client=us, remove=False).order_by('-date')
        not_rep = RepairmanNotifications.objects.filter(repairman=us, seen=False).count()
        not_cli = ClientNotifications.objects.filter(client=us, seen=False).count()
        mess_cli = ClientMessage.objects.filter((Q(client=us) | Q(sender=us)) & Q(seen=False)).order_by("-date")
        mess_cli_c = ClientMessage.objects.filter(Q(client=us) & Q(seen_notif=False)).count()

        context_data['f_hired'] = f_hired
        context_data['seen_r'] = reqq_seen
        context_data['cnt'] = cnt
        context_data['act_cnt'] = act_cnt
        context_data['not_r'] = not_r
        context_data['not_c'] = not_c
        context_data['not_rep'] = not_rep
        context_data['not_cli'] = not_cli
        context_data['mess_cli'] = mess_cli
        context_data['mess_cli_c'] = mess_cli_c
        context_data['filter_form'] = TopRatedFilter(self.request.GET, queryset=self.get_queryset())

        return context_data


class RepairmanFeedbacksListView(LoginRequiredMixin, ListView):
    model = Rate
    template_name = 'need_a_help_app/repairman_feedbacks.html'
    context_object_name = 'feeds'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs.get('pk'))
        return Rate.objects.filter(repairman=user).order_by('-date')

    def get_context_data(self, **kwargs):
        context_data = super(RepairmanFeedbacksListView, self).get_context_data(**kwargs)

        users = User.objects.all()
        us = self.request.user
        not_r = RepairmanNotifications.objects.filter(repairman=us, remove=False).order_by('-date')
        not_rep = RepairmanNotifications.objects.filter(repairman=us, seen=False).count()
        mess_cli = ClientMessage.objects.filter((Q(client=us) | Q(sender=us)) & Q(seen=False)).order_by("-date")
        mess_cli_c = ClientMessage.objects.filter(Q(client=us) & Q(seen_notif=False)).count()

        context_data['us'] = users
        context_data['not_r'] = not_r
        context_data['not_rep'] = not_rep
        context_data['mess_cli'] = mess_cli
        context_data['mess_cli_c'] = mess_cli_c

        return context_data
