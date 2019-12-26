from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
        path('upload/',views.upload_video,name='upload_video'),
        path('delete/', views.delete_video, name='delete_video'),
]
