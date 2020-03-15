from posts import views
from django.urls import path

urls = [
    path(r'add/', views.PostFormView.as_view(), name="add_post"),
    path(r'<slug:slug>/', views.post_detail, name='post_detail')
]
