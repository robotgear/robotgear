from teams import views
from django.urls import path

urls = [
    path(r'add_team', views.add_team_view, name='addTeam'),
    path(r'new_team', views.new_team_view, name='newTeam'),
    path(r'delete_team/<str:comp>/<str:team>', views.delete_team_view, name='deleteTeam'),
    path(r'edit_team/<str:comp>/<str:team>', views.edit_team_view, name='editTeam'),
    path(r'<str:comp>/<str:team>', views.team_detail, name='teamDetail')
]
