"""robotgear URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include
from django.urls import path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from market import views
import debug_toolbar

urlpatterns = [
    path(r'admin/', admin.site.urls),
    path(r'', views.index, name='index'),
    path(r'login/', views.loginView, name='login'),
    path(r'logout/', views.logoutView, name='logout'),
    path(r'register/', views.registerView, name='register'),
    path(r'activate/<str:uidb64>/<str:token>/', views.activate, name="activate"),
    path(r'__debug__/', include(debug_toolbar.urls))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
