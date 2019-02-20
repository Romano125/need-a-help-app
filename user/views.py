from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import (
    UserRegisterForm,
    ProfileRegisterForm,
    UserUpdateForm,
    ProfileUpdateForm
)
from django.contrib.auth.decorators import login_required


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
        'form_p': form_p
    }

    return render(request, 'user/register.html', context)


@login_required  # decorator dodaje funkcionalnost nasoj funkciji
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'You have updated your account!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    args = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'user/profile.html', args)
