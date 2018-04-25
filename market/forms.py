from django import forms
from django.contrib.auth.forms import UserCreationForm


class RegisterForm(UserCreationForm):
	email = forms.EmailField()
	first_name = forms.CharField(required=False)
	last_name = forms.CharField(required=False)
