from rest_framework import serializers
from django.contrib.auth.models import User


class LanguageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


