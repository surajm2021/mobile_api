import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import utc


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_no = models.IntegerField()
    application_id = models.CharField(max_length=50, null=True)
    is_verify = models.BooleanField(default=False)
    tags = models.CharField(max_length=50, null=True)
    channel_id = models.IntegerField(default=0, null=True)
    liked = models.CharField(max_length=255, default="")
    disliked = models.CharField(max_length=255, default="")

    def __str__(self):
        return self.user.username


class Otp(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    OTP = models.IntegerField(null=True)
    attempts = models.IntegerField(default=5)
    time_generate_otp = models.DateTimeField(auto_now_add=True, blank=True)

    def get_time_diff(self):
        if self.time_generate_otp:
            now = datetime.datetime.utcnow().replace(tzinfo=utc)
            timediff = now - self.time_generate_otp
            return timediff.total_seconds()

    def __str__(self):
        return self.user.username
