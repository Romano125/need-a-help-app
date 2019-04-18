from django import forms
from crispy_forms.helper import FormHelper


class ComposeForm(forms.Form):

    message = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        )
    )

    def __init__(self, *args, **kwargs):
        super(ComposeForm, self).__init__(auto_id=True, *args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
