from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
        path('create_channel/',views.create_channel,name='create_channel'),
]
