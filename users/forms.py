from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import User


class RegisterForm(UserCreationForm):

	class Meta:
		model = User
		layout = [

		]

