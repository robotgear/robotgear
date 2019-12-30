from users import views
from django.urls import path

urls = [
    path(r'login/', views.login_view, name='login'),
    path(r'logout/', views.logout_view, name='logout'),
    path(r'register/', views.register_view, name='register'),
    path(r'activate/<str:uidb64>/<str:token>/', views.activate_view, name="activate"),
    path(r'reactivate/<str:username>', views.reactivate_view, name="reactivate"),
    path(r'reset/', views.reset_view, name='reset'),
    path(r'reset/<str:uidb64>/<str:token>', views.reset_link_view, name='resetLink'),
    path(r'settings/', views.settings_view, name='settings'),
    path(r'settings/reset_password', views.reset_logged_in_view, name='resetLoggedInLink'),
    path(r'settings/reset_email', views.change_email_view, name='resetEmail'),
    path(r'settings/reset_username', views.change_username_view, name='resetUsername'),
    path(r'settings/edit_relationship', views.edit_relationship_view, name='editRelationship'),
    path(r'settings/edit_desc',views.update_desc, name='updateDesc'),
    path(r'settings/edit_avatar',views.upload_avatar, name='updateAvatar'),
    path(r'users/<str:username>', views.user_detail, name='userDetail')
]
