from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Requests
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


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

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(auto_id=True, *args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'placeholder': 'mickey',
            'autocomplete': 'off',
            'class': 'form-control',
            'required': True,
        })
        self.fields['first_name'].widget.attrs.update({
            'placeholder': 'Mirko',
            'autocomplete': 'off',
            'class': 'form-control',
            'required': True,
        })
        self.fields['last_name'].widget.attrs.update({
            'placeholder': 'Mirkic',
            'autocomplete': 'off',
            'class': 'form-control',
            'required': True,
        })
        self.fields['email'].widget.attrs.update({
            'placeholder': 'mirko.mirkic67@gmail.com',
            'autocomplete': 'off',
            'class': 'form-control',
            'required': True,
        })
        self.fields['password1'].widget.attrs.update({
            'placeholder': '*******',
            'autocomplete': 'off',
            'class': 'form-control',
            'required': True,
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': '*******',
            'autocomplete': 'off',
            'class': 'form-control',
            'required': True,
        })

        self.helper = FormHelper()


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
        self.fields['address'].widget.attrs.update({
            'placeholder': 'Enter a location',
            'class': 'form-control',
            'required': True,
        })
        self.fields['birth_date'].widget.attrs.update({
            'placeholder': 'YYYY-MM-DD',
            'autocomplete': 'off',
            'class': 'form-control',
            'required': True,
        })
        self.fields['gender'].widget.attrs.update({
            'placeholder': 'Choose gender',
            'autocomplete': 'off',
            'class': 'form-control',
            'required': True,
        })
        self.fields['role'].widget.attrs.update({
            'placeholder': 'Choose role',
            'autocomplete': 'off',
            'class': 'form-control',
            'required': True,
        })


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

        self.fields['phone_number'].widget.attrs.update({
            'placeholder': '+385 98 546 9523',
            'required': True,
        })
        self.fields['costs'].widget.attrs.update({
            'placeholder': 'Price of your services',
            'required': True,
        })
        self.fields['profession'].widget.attrs.update({
            'placeholder': 'Plumber',
            'required': True,
        })
        self.fields['knowledges'].widget.attrs.update({
            'placeholder': 'Your extra knowledges',
            'required': True,
        })


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

        self.fields['phone_number'].widget.attrs.update({
            'placeholder': '+385 98 546 9523',
            'required': True,
        })


class RequestsForm(forms.ModelForm):
    class Meta:
        model = Requests
        exclude = ('user', 'date', 'visible')

    def __init__(self, *args, **kwargs):
        super(RequestsForm, self).__init__(auto_id=True, *args, **kwargs)

        self.fields['job_title'].widget.attrs.update({
            'placeholder': 'Help with cleaning',
            'required': True,
        })
        self.fields['required_knowledges'].widget.attrs.update({
            'placeholder': 'Knowledges a repairman must have',
            'required': True,
        })
        self.fields['price'].widget.attrs.update({
            'placeholder': 'How much will you pay for this job?',
            'required': True,
        })
        self.fields['address'].widget.attrs.update({
            'placeholder': 'Enter a location',
            'required': True,
        })
        self.fields['job_description'].widget.attrs.update({
            'placeholder': 'Describe job in few tips',
            'required': True,
        })
