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
from users.urls import urls as users_urls
from teams.urls import urls as teams_urls
from posts.urls import urls as posts_urls
from robotgear.views import IndexView, TermsAndConditions

urlpatterns = [
    path(r'', IndexView.as_view(), name='index'),
    path(r'terms/', TermsAndConditions.as_view(), name='terms'),
    path(r'contact/', TermsAndConditions.as_view(), name='contact'),
    path(r'admin/', admin.site.urls),
    path(r'user/', include(users_urls)),
    path(r'teams/', include(teams_urls)),
    path(r'posts/', include(posts_urls))
]

if settings.DEBUG :
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    import debug_toolbar

    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns
