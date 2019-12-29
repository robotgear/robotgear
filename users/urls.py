from users import views
from django.urls import path

urls = [
    path(r'login/', views.loginView, name='login'),
    path(r'logout/', views.logoutView, name='logout'),
    path(r'register/', views.registerView, name='register'),
    path(r'activate/<str:uidb64>/<str:token>/', views.activate, name="activate"),
    path(r'reactivate/<str:username>', views.reactivate, name="reactivate"),
    path(r'reset/', views.resetView, name='reset'),
    path(r'reset/<str:uidb64>/<str:token>', views.resetLinkView, name='resetLink'),
    path(r'settings/', views.settingsView, name='settings'),
    path(r'settings/reset_password', views.resetLoggedInView, name='resetLoggedInLink'),
    path(r'settings/reset_email', views.changeEmailView, name='resetEmail'),
    path(r'settings/reset_username', views.changeUsernameView, name='resetUsername'),
    path(r'settings/edit_relationship', views.editRelationshipView, name='editRelationship'),
    path(r'settings/edit_desc',views.updateDesc, name='updateDesc'),
    path(r'settings/edit_avatar',views.uploadAvatar, name='updateAvatar'),
    path(r'users/<str:username>', views.userDetail, name='userDetail')
]
