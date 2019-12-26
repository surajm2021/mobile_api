from rest_framework import serializers
from .models import Employee
from django.contrib.auth.models import User


class LanguageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Employee
        fields = ['phone_no']

    class Meta:
        model = User
        fields = '__all__'


