from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout, password_validation
from django.core.exceptions import ValidationError
from market.models import User
from django.contrib import messages
from django.shortcuts import redirect
from django.db import IntegrityError
from django.utils.encoding import force_text, force_bytes
from django.utils.http import urlsafe_base64_decode
from market.tokens import account_activation_token
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from .forms import *

# Create your views here.

def index(request):
	return render(request, 'index.html')

def loginView(request):
	if request.user.is_authenticated:
		return redirect(index)
	if request.method == "POST":
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			return redirect(index)
		else:
			messages.error(request, "Incorrect login details.")
			return render(request, 'login.html')
	else:
		return render(request, 'login.html')


def logoutView(request):
	if request.user.is_authenticated:
		logout(request)
		return redirect(index)
	else:
		return redirect(loginView)


def registerView(request):
	# if request.method == "POST":
	# 	form = RegisterForm(request.POST)
	# 	if form.is_valid():
	# 		user = User(username=form.username, email=form.email, first_name=form.first_name, last_name=form.last_name)
	# 		try:
	# 			password_validation.validate_password(form.password,user,password_validators='AUTH_PASSWORD_VALIDATORS')
	# 			user.set_password(form.password)
	# 		except ValidationError:
	# 			form.password = ""
	# 			messages.error(request, "That password is not valid. ")
	# 			return render(request, 'register.html', form=form)
	# 		current_site = get_current_site(request)
	# 		subject = 'Activate Your MySite Account'
	# 		message = render_to_string('activiation_email.html', {
	#  			'user'  : user,
	# 			'domain': current_site.domain,
 	# 			'uid'   : force_text(urlsafe_base64_encode(force_bytes(user.pk))),
	#  			'token' : account_activation_token.make_token(user),
	#  		})
	# 		user.email_user(subject, message)
	# 		messages.success(request, "Your account has been created. Please check your email.")
	# 		return redirect(index)
	# 	else:
	# 		form = RegisterForm
	# 		messages.error(request, "Please fully fill out all required fields.")
	# 		return render(request, "register.html", {'form':form})
	# else:
	# 	form = RegisterForm
	# 	return render(request, "register.html", {'form':form})


	if request.user.is_authenticated:
		return redirect(index)
	if request.method == "POST":
		username = request.POST.get('username')
		password = request.POST.get('password')
		email = request.POST.get('email')

		try:
			password_validation.validate_password(password)
		except ValidationError:
			messages.error(request, "Invalid password.")
			return render(request, 'register.html')

		try:
			user = User.objects.create_user(username,email,password)

		except IntegrityError:
			messages.error(request, "That username is taken.")
			return render(request, 'register.html')

		if user is not None:
			current_site = get_current_site(request)
			subject = 'Activate Your MySite Account'
			message = render_to_string('activiation_email.html', {
				'user'  : user,
				'domain': current_site.domain,
				'uid'   : force_text(urlsafe_base64_encode(force_bytes(user.pk))),
				'token' : account_activation_token.make_token(user),
			})
			user.email_user(subject, message)
			messages.success(request, "Your account has been created. Please check your email.")
			return redirect(index)
		else:
			messages.error(request, "An error has occurred, please try again.")
			return render(request, 'register.html')
	else:
		return render(request, 'register.html')


def activate(request, uidb64, token):
	try:
		uid = force_text(urlsafe_base64_decode(uidb64))
		user = User.objects.get(pk=uid)
	except (TypeError, ValueError, OverflowError, User.DoesNotExist):
		user = None

	if user is not None and account_activation_token.check_token(user, token):
		user.is_active = True
		user.email_confirmed = True
		user.save()
		login(request, user)
		messages.success(request, "Your account has been activated.")
		return redirect('index')
	else:
		messages.error(request, "An error occurred when trying to validate your email. ")
		return render(request, index)