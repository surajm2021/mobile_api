from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('create_channel/', views.create_channel, name='create_channel'),
    path('delete/', views.delete_channel, name='delete_channel'),
    path('create_course/', views.create_course, name='create_course'),
    path('update_or_create_course_session/', views.update_or_create_course_session, name='update_course_session'),
    path('delete_course/', views.delete_course, name='delete_course'),
    path('delete_session/', views.delete_session, name='delete_session'),
    path('delete_video_from_session/', views.delete_video_from_session, name='delete_video_from_session'),
]
