from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Requests
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, HTML, Field


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
            'class': 'form-control',
            'autocomplete': 'off',
            'required': True,
            'maxlength': 300
        })
        self.fields['first_name'].widget.attrs.update({
            'placeholder': 'Mirko',
            'autocomplete': 'off',
            'class': 'form-control',
            'required': True,
            'maxlength': 300
        })
        self.fields['last_name'].widget.attrs.update({
            'placeholder': 'Mirkic',
            'autocomplete': 'off',
            'class': 'form-control',
            'required': True,
            'maxlength': 300
        })
        self.fields['email'].widget.attrs.update({
            'placeholder': 'mirko.mirkic67@gmail.com',
            'autocomplete': 'off',
            'class': 'form-control',
            'required': True,
            'maxlength': 300
        })
        self.fields['password1'].widget.attrs.update({
            'placeholder': '*******',
            'autocomplete': 'off',
            'class': 'form-control',
            'required': True,
            'maxlength': 300
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': '*******',
            'autocomplete': 'off',
            'class': 'form-control',
            'required': True,
            'maxlength': 300
        })

        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.form_style = 'inline'
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="input-group-text" style="height: 38px;"><i class="fas fa-user"></i></span>'),
                    css_class='input-group-append'
                ),
                Field('username', css_class="controls col-md-12 col-xs-7"),
                css_class='input-group mb-2'
            ),
            Div(
                Div(
                    HTML('<span class="input-group-text" style="height: 38px;"><i class="fas fa-user"></i></span>'),
                    css_class='input-group-append'
                ),
                Field('first_name', css_class="controls col-md-12 col-xs-7"),
                css_class='input-group mb-2'
            ),
            Div(
                Div(
                    HTML('<span class="input-group-text" style="height: 38px;"><i class="fas fa-user"></i></span>'),
                    css_class='input-group-append'
                ),
                Field('last_name', css_class="controls col-md-12 col-xs-7"),
                css_class='input-group mb-2'
            ),
            Div(
                Div(
                    HTML('<span class="input-group-text" style="height: 38px;"><i class="fas fa-envelope"></i></span>'),
                    css_class='input-group-append'
                ),
                Field('email', css_class="controls col-md-12 col-xs-7"),
                css_class='input-group mb-2'
            ),
            Div(
                Div(
                    HTML('<span class="input-group-text" style="height: 38px;"><i class="fas fa-key"></i></span>'),
                    css_class='input-group-append'
                ),
                Field('password1', css_class="controls col-md-12 col-xs-7"),
                css_class='input-group mb-2'
            ),
            Div(
                Div(
                    HTML('<span class="input-group-text" style="height: 38px;"><i class="fas fa-key"></i></span>'),
                    css_class='input-group-append'
                ),
                Field('password2', css_class="controls col-md-12 col-xs-7"),
                css_class='input-group mb-2'
            ),
        )


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
            'maxlength': 300
        })
        self.fields['birth_date'].widget.attrs.update({
            'placeholder': 'YYYY-MM-DD',
            'autocomplete': 'off',
            'class': 'form-control',
            'required': True,
            'maxlength': 300
        })
        self.fields['gender'].widget.attrs.update({
            'placeholder': 'Choose gender',
            'autocomplete': 'off',
            'class': 'form-control',
            'required': True,
            'maxlength': 300
        })
        self.fields['role'].widget.attrs.update({
            'placeholder': 'Choose role',
            'autocomplete': 'off',
            'class': 'form-control',
            'required': True,
            'maxlength': 300
        })

        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.form_style = 'inline'
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="input-group-text" style="height: 38px;"><i class="fas fa-map-marker-alt"></i></span>'),
                    css_class='input-group-append'
                ),
                Field('address', css_class="controls col-md-12 col-xs-7"),
                css_class='input-group mb-2'
            ),
            Div(
                Div(
                    HTML('<span class="input-group-text" style="height: 38px;"><i class="fas fa-calendar"></i></span>'),
                    css_class='input-group-append'
                ),
                Field('birth_date', css_class="controls col-md-12 col-xs-7"),
                css_class='input-group mb-2'
            ),
            HTML('<span class="pb-2" style="color: #d9d9d9">Select gender:</span>'),
            Div(
                Div(
                    HTML('<span class="input-group-text" style="height: 38px;"><i class="fas fa-user"></i></span>'),
                    css_class='input-group-append'
                ),
                Field('gender', css_class="controls col-md-12 col-xs-7"),
                css_class='input-group mb-2'
            ),
            HTML('<span class="pb-2" style="color: #d9d9d9">Select role:</span>'),
            Div(
                Div(
                    HTML('<span class="input-group-text" style="height: 38px;"><i class="fas fa-user"></i></span>'),
                    css_class='input-group-append'
                ),
                Field('role', css_class="controls col-md-12 col-xs-7"),
                css_class='input-group mb-2'
            ),
        )


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
            'maxlength': 300
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
