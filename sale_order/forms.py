from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User


class CreateUserForm(UserCreationForm):
    # phone = forms.FloatField()
    # address = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

        # def save(self, commit=True):
        #     user = super(CreateUserForm, self).save(commit=False)
        #     user.phone = self.cleaned_data["phone"]
        #     user.address = self.cleaned_data["address"]
        #     if commit:
        #         user.save()
        #     return user


class MyPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for fieldname in ['old_password', 'new_password1', 'new_password2']:
            self.fields[fieldname].widget.attrs = {'class': 'form-control'}


