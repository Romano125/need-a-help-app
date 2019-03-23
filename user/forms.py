from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Requests


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

    def __init__(self, *args, **kwargs):
        super(ProfileRegisterForm, self).__init__(auto_id=True, *args, **kwargs)


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
            'photo'
        ]

    def __init__(self, *args, **kwargs):
        super(RepairmanUpdateForm, self).__init__(auto_id=True, *args, **kwargs)


class ClientUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'gender',
            'address',
            'birth_date',
            'phone_number',
            'photo'
        ]

    def __init__(self, *args, **kwargs):
        super(ClientUpdateForm, self).__init__(auto_id=True, *args, **kwargs)


class RequestsForm(forms.ModelForm):
    class Meta:
        model = Requests
        exclude = ('user', 'date', 'visible')

    def __init__(self, *args, **kwargs):
        super(RequestsForm, self).__init__(auto_id=True, *args, **kwargs)
