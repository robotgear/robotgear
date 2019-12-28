from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import User


class UserDescriptionForm(forms.Form):
	description = forms.CharField(max_length=400, widget=forms.Textarea)


class UserAvatarForm(forms.Form):
	avatar = forms.ImageField()
