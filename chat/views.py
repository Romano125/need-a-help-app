from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import FormMixin
from django.db.models import Q

from django.views.generic import DetailView, ListView
from django.contrib.auth.models import User

from .forms import ComposeForm
from .models import Thread, ChatMessage
from user.models import ClientNotifications, RepairmanNotifications


class InboxView(LoginRequiredMixin, ListView):
    # odkomentiraj model = Thread
    template_name = 'chat/inbox.html'
    context_object_name = 'users'
    #paginate_by = 3

    def get_queryset(self):
        # return Thread.objects.by_user(self.request.user).order_by('-timestamp') - točno
        # return Thread.objects.filter(Q(first=self.request.user)|Q(second=self.request.user)).order_by('-timestamp').distinct()
        return ChatMessage.objects.filter(Q(thread__first=self.request.user) | Q(thread__second=self.request.user)).order_by('-timestamp').distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        us = self.request.user
        thrd = Thread.objects.filter(Q(first=self.request.user) | Q(second=self.request.user))

        not_r = RepairmanNotifications.objects.filter(repairman=us, remove=False).order_by('-date')
        not_c = ClientNotifications.objects.filter(client=us, remove=False).order_by('-date')
        not_rep = RepairmanNotifications.objects.filter(repairman=us, seen=False).count()
        not_cli = ClientNotifications.objects.filter(client=us, seen=False).count()

        # users =  ChatMessage.objects.by_user(us).order_by('-timestamp').distinct()

        context['not_r'] = not_r
        context['not_c'] = not_c
        context['not_rep'] = not_rep
        context['not_cli'] = not_cli
        context['th'] = thrd
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
        context['form'] = self.get_form()
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
        ChatMessage.objects.create(user=user, thread=thread, message=message)
        return super().form_valid(form)
