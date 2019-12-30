"""Auth URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.home, name="home_page"),
    path("register_user/", views.register, name="register"),
    path("login_user/", views.login_user, name="login_user"),
    path('logout_user/',views.logout,name='logout'),
    path('profile_user/',views.profileinfo,name='profile'),
    path('login_user_by_otp/',views.verify_opt,name='verifyotp'),
    path('delete_user/', views.delete_user, name='delete_user'),

    path('verify_otp_reset/', views.verify_otp_reset, name='verify_otp_reset'),
    path('resend_reset_otp/', views.resend_reset_otp, name='resend_reset_otp'),
    path('password_change/', views.password_change, name='password_change'),
    path('mobile_no_change/',views.mobile_no_change,name='mobile_no_change'),

]
