from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2'
        ]


class ProfileRegisterForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'address',
            'birth_date',
            'gender',
            'role'
        ]


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email'
        ]


class RepairmanUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'gender',
            'address',
            'birth_date',
            'phone_number',
            'costs',
            'profession',
            'knowledges',
            'role',
            'photo'
        ]


class ClientUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'gender',
            'address',
            'birth_date',
            'phone_number',
            'role',
            'photo'
        ]
