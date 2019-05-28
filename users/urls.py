from users import views
from django.urls import path

urls = [
    path(r'login/', views.loginView, name='login'),
    path(r'logout/', views.logoutView, name='logout'),
    path(r'register/', views.registerView, name='register'),
    path(r'activate/<str:uidb64>/<str:token>/', views.activate, name="activate"),
]