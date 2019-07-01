from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout, password_validation
from django.core.exceptions import ValidationError
from users.models import User
from django.contrib import messages
from django.shortcuts import redirect
from django.db import IntegrityError
from django.utils.encoding import force_text, force_bytes
from django.utils.http import urlsafe_base64_decode
from users.tokens import account_activation_token
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site

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
			message = render_to_string('email/activiation_email.html', {
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


def resetView(request):
	if request.user.is_authenticated:
		return redirect(request, index)
	if request.method == "GET":
		return render(request, 'reset.html')
	username = request.POST.get('username')
	try:
		user = User.objects.get(username=username)
	except User.DoesNotExist:
		messages.error(request, "That user does not exist.")
		return render(request, 'reset.html')
	current_site = get_current_site(request)
	subject = 'Reset Your RobotGear Password'
	message = render_to_string('reset_email.html', {
		'user': user,
		'domain': current_site.domain,
		'uid': force_text(urlsafe_base64_encode(force_bytes(user.pk))),
		'token': default_token_generator.make_token(user),
	})
	user.email_user(subject, message)
	messages.success(request, "A link has been sent to you. Please check your email.")
	return render(request, 'reset.html')


def resetLinkView(request, uidb64, token):
	try:
		uid = force_text(urlsafe_base64_decode(uidb64))
		user = User.objects.get(pk=uid)
	except (TypeError, ValueError, OverflowError, User.DoesNotExist):
		user = None
	if user is not None and default_token_generator.check_token(user, token):
		if request.method == "GET":
			return render(request, 'email/reset_pass_entry.html', context={'username': user.username})
		elif request.method == "POST":
			password = request.POST.get("password")
			try:
				password_validation.validate_password(password)
			except ValidationError:
				messages.error(request, "Invalid password.")
				return render(request, 'email/reset_pass_entry.html')
			user.set_password(password)
			user.save()
			messages.success(request, "Password changed correctly.")
			return redirect('login')
	else:
		messages.error(request, "An error occurred when trying to validate your email. ")
		return render(request, 'reset.html')


def settingsView(request):
	if request.user.is_authenticated:
		return render(request, 'settings.html')
	else:
		return redirect(loginView)
