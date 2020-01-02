from django.urls import path, include
from . import views

urlpatterns = [
        path('upload/',views.upload_video,name='upload_video'),
        path('delete/', views.delete_video, name='delete_video'),
        path('like_video/', views.like_video, name='like_video'),
        path('dislike_video/', views.dislike_video, name='dislike_video'),
        path('trending_video/', views.trending_video, name='trending_video'),

]
