from users import views
from django.urls import path

urls = [
    path(r'', views.IndexView.as_view(), name='index'),
    path(r'terms/', views.TermsAndConditions.as_view(), name='terms'),
    path(r'contact/', views.TermsAndConditions.as_view(), name='contact'),
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
    path(r'settings/add_team', views.addTeamView, name='addTeam'),
    path(r'settings/new_team', views.newTeamView, name='newTeam'),
    path(r'settings/delete_team/<str:comp>/<str:team>', views.deleteTeamView, name='deleteTeam')
]