from django.urls import path
from . import views

urlpatterns = [
    path('', views.video_page, name='home'),
    path('video/', views.video_page, name='video_page'),
    path('video_feed/', views.video_feed, name='video_feed'),
]
