from django.urls import path
from . import views
from pages.views import index, books, library, login

urlpatterns = [
    path('', index, name='home'),
    path('login/', login, name='login'),
    path('library/', library, name='library'),
    path('books/', books, name='books'),
    path('video/', views.video_page, name='video_page'),
    path('video_feed/', views.video_feed, name='video_feed'),
]
