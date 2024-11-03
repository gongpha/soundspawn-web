from django import forms

from .models import Sound

class BootstrapForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs = {
                'class': 'form-control'
            }

class LoginForm(BootstrapForm):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

class SignUpForm(BootstrapForm):
    username = forms.CharField(label='Username', max_length=100)
    email = forms.EmailField(label='Email', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

class EditProfileForm(BootstrapForm):
    username = forms.CharField(label='Username', max_length=100)
    email = forms.EmailField(label='Email', max_length=100)

    new_pic = forms.ImageField(label='New Profile Picture', required=False)