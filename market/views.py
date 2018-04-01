from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from market.models import User
from django.contrib import messages
from django.shortcuts import redirect

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
			messages.success(request, "Welcome back, {}".format(user.username))
			return redirect(index)
		else:
			messages.error(request, "Inorrect login details.")
			return render(request,'login.html')
	else:
		return render(request, 'login.html')

def logoutView(request):
	if request.user.is_authenticated:
		logout(request)
		messages.success(request, "You have been logged out")
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
		first_name = request.POST.get('first_name')
		last_name = request.POST.get('last_name')
		try:
			user = User.objects.create_user(username,email,password, first_name=first_name,last_name=last_name)
		except ValueError as e:
			error = {
				"The given username must be set": "Please provide a username"
			}
			try:
				messages.error(request, error[str(e)])
			except ValueError:
				messages.error(request, "An unknown error has occurred:{}".format(e))
			return render(request, 'register.html')
		if user is not None:
			login(request, user)
			messages.success(request, "Your account has been created. Please check your email.")
			return redirect(index)
		else:
			messages.error(request, "An error has occurred, please try again.")
			return render(request, 'register.html')
	else:
		return render(request, 'register.html')