from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import (
    UserRegisterForm,
    ProfileRegisterForm,
    UserUpdateForm,
    RepairmanUpdateForm,
    ClientUpdateForm
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import ClientNotifications, RepairmanNotifications
from need_a_help import settings


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        form_p = ProfileRegisterForm(request.POST)
        if form.is_valid() and form_p.is_valid():
            user = form.save()
            user.profile.address = form_p.cleaned_data.get('address')
            user.profile.birth_date = form_p.cleaned_data.get('birth_date')
            user.profile.role = form_p.cleaned_data.get('role')
            user.profile.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You are able to login!')
            return redirect('login')
    else:
        form = UserRegisterForm()
        form_p = ProfileRegisterForm()

    context = {
        'form': form,
        'form_p': form_p,
        'api_key': settings.GOOGLE_MAPS_API_KEY
    }

    return render(request, 'user/register.html', context)


@login_required  # decorator dodaje funkcionalnost nasoj funkciji
def profile(request, log):
    user = User.objects.filter(id=log).first()

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if user.profile.role == 'repairman':
            p_form = RepairmanUpdateForm(request.POST,
                                         request.FILES,
                                         instance=request.user.profile)
        else:
            p_form = ClientUpdateForm(request.POST,
                                      request.FILES,
                                      instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'You have updated your account!')
            return redirect('profile', log=user.id)
    else:
        u_form = UserUpdateForm(instance=request.user)
        if user.profile.role == 'repairman':
            p_form = RepairmanUpdateForm(instance=request.user.profile)
        else:
            p_form = ClientUpdateForm(instance=request.user.profile)

    us = request.user
    not_r = RepairmanNotifications.objects.filter(repairman=us, remove=False).order_by('-date')
    not_c = ClientNotifications.objects.filter(client=us, remove=False).order_by('-date')
    not_rep = RepairmanNotifications.objects.filter(repairman=user, seen=False).count()
    not_cli = ClientNotifications.objects.filter(client=user, seen=False).count()

    args = {
        'u_form': u_form,
        'p_form': p_form,
        'not_c': not_c,
        'not_r': not_r,
        'not_cli': not_cli,
        'not_rep': not_rep,
        'api_key': settings.GOOGLE_MAPS_API_KEY
    }

    return render(request, 'user/profile.html', args)
