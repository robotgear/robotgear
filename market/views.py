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
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			return redirect(index)
		else:
			messages.error(request, "Inorrect login details.")
			return render(request,'login.html')
	else:
		return render(request, 'login.html')

def logoutView(request):
	if request.user.is_authenticated:
		logout(request)
		return redirect(index)
	else:
		return redirect(loginView)
