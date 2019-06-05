from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import FormMixin
from django.db.models import Q
from datetime import datetime

from django.views.generic import DetailView, ListView
from django.contrib.auth.models import User

from .forms import ComposeForm
from .models import Thread, ChatMessage
from  user.models import ClientMessage
from user.models import ClientNotifications, RepairmanNotifications


class InboxView(LoginRequiredMixin, ListView):
    # odkomentiraj model = Thread
    template_name = 'chat/inbox.html'
    context_object_name = 'users'
    #paginate_by = 3

    def get_queryset(self):
        #return Thread.objects.by_user(self.request.user).order_by('-timestamp')
        return Thread.objects.filter(Q(first=self.request.user)|Q(second=self.request.user)).order_by('-updated')

        #return ChatMessage.objects.filter(Q(thread__first=self.request.user) | Q(thread__second=self.request.user)).order_by('-timestamp').distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        us = self.request.user
        thrd = Thread.objects.filter(Q(first=self.request.user) | Q(second=self.request.user))

        not_r = RepairmanNotifications.objects.filter(repairman=us, remove=False).order_by('-date')
        not_c = ClientNotifications.objects.filter(client=us, remove=False).order_by('-date')
        not_rep = RepairmanNotifications.objects.filter(repairman=us, seen=False).count()
        not_cli = ClientNotifications.objects.filter(client=us, seen=False).count()
        mess_cli = ClientMessage.objects.filter(client=us,seen=False).order_by('-date')
        mess_cli_c = ClientMessage.objects.filter(client=us,seen=False).count()

        # users =  ChatMessage.objects.by_user(us).order_by('-timestamp').distinct()

        context['not_r'] = not_r
        context['not_c'] = not_c
        context['not_rep'] = not_rep
        context['not_cli'] = not_cli
        context['th'] = thrd
        context['mess_cli'] = mess_cli
        context['mess_cli_c'] = mess_cli_c
        # context['users'] = users

        return context


class ThreadView(LoginRequiredMixin, FormMixin, DetailView):
    template_name = 'chat/thread.html'
    form_class = ComposeForm

    def get_success_url(self):
        #user = self.request.user
        other_username = self.kwargs.get("username")
        return reverse_lazy('messages', kwargs={'username': other_username})

    def get_queryset(self):
        return Thread.objects.by_user(self.request.user)

    def get_object(self):
        other_username = self.kwargs.get("username")
        obj, created = Thread.objects.get_or_new(self.request.user, other_username)
        if obj == None:  # is?
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        us = self.request.user

        other_username = self.kwargs.get("username")
        other_object = User.objects.filter(username=other_username)[0]
        not_seen_notif = ClientMessage.objects.filter(client=us,seen_notif=False, sender=other_object)
        #not_seen_notif_count = ClientMessage.objects.filter(client=us,seen=False, sender=other_object).count()
        for n in not_seen_notif:
            n.seen_notif = True
            n.save()


        not_seen = ClientMessage.objects.filter((Q(client=us, sender=other_object) | Q(sender=us, client=other_object)) & Q(seen=False))
        not_seen_count = ClientMessage.objects.filter((Q(client=us, sender=other_object) | Q(sender=us, client=other_object)) & Q(seen=False)).count()
        not_seen_count -= 1
        i = 0
        for m in not_seen:
            if i != not_seen_count:
                m.seen = True
                m.save()
            i += 1
        



        not_r = RepairmanNotifications.objects.filter(repairman=us, remove=False).order_by('-date')
        not_c = ClientNotifications.objects.filter(client=us, remove=False).order_by('-date')
        not_rep = RepairmanNotifications.objects.filter(repairman=us, seen=False).count()
        not_cli = ClientNotifications.objects.filter(client=us, seen=False).count()
        mess_cli = ClientMessage.objects.filter((Q(client=us) | Q(sender=us)) & Q(seen=False)).order_by("-date")
        mess_cli_c = ClientMessage.objects.filter(Q(client=us) & Q(seen_notif=False)).count()

        thr = Thread.objects.filter(Q(first=self.request.user)|Q(second=self.request.user)).order_by('-updated')

        context['form'] = self.get_form()
        context['not_r'] = not_r
        context['not_c'] = not_c
        context['not_rep'] = not_rep
        context['not_cli'] = not_cli
        context['inbox'] = thr
        context['mess_cli'] = mess_cli
        context['mess_cli_c'] = mess_cli_c

        return context


    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        thread = self.get_object()
        user = self.request.user
        message = form.cleaned_data.get("message")
        mess = ChatMessage.objects.create(user=user, thread=thread, message=message)
        #thr = Thread.objects.filter(Q(first=self.request.user) | Q(second=self.request.user)).order_by('-updated')[0]
        thr = thread
        thr.latestMessage = message
        thr.save()
        if (thread.first == user):
            not_usr = thread.second
        else :
            not_usr = thread.first

        url1 = f'{ reverse("messages", kwargs={"username": user}) }'
        url2 = f'{ reverse("messages", kwargs={"username": not_usr}) }'
        """
        noti = ClientMessage.objects.filter(client=not_usr,seen=False, sender=user)
        i = 0
        for n in noti :
            if i != 0:
                n.seen = True
                n.save()
            i += 1    
        """
        ClientMessage.objects.create(client= not_usr, message = mess, url_to_go_client = url2, url_to_go_sender=url1, sender=user)

        return super().form_valid(form)
#boto3 1.5.0
#django storages 1.6.3
