from PIL import Image
from django.db import models
from video.models import video_class


# from video.models import video_class


class channel_model(models.Model):
    logo = models.ImageField(upload_to='channel_logo')
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    followers = models.IntegerField(default=0)
    total_views = models.IntegerField(default=0)
    video_id = models.CharField(max_length=100, null=True, default="")
    courses_id = models.CharField(max_length=50, null=True)
    playlist = models.CharField(max_length=50, default="")

    def __str__(self):
        return str(self.id) + " " + self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.logo.path)
        if img.height > 100 or img.width > 100:
            output_size = (100, 100)
            img.thumbnail(output_size)
            img.save(self.logo.path)


class course(models.Model):
    channel_id = models.IntegerField()
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100)
    description = models.CharField(max_length=100,null=True)
    requirement = models.CharField(max_length=100,null=True)
    level = models.CharField(max_length=100,null=True)
    categary = models.CharField(max_length=100,null=True)
    tags = models.CharField(max_length=100, null=True)
    price = models.IntegerField(default=0)
    session_id = models.CharField(max_length=255, null=True)
    certificate: models.IntegerField(default='certificate.png', null=True)

    def __str__(self):
        return str(self.id) + " " + self.title


class course_session(models.Model):
    title = models.CharField(max_length=250, null=True)
    video_id = models.CharField(max_length=250, null=True)

    def __str__(self):
        return str(self.id)
