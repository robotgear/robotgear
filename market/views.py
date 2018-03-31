from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
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
		pass
	else:
		return render(request, 'register.html')