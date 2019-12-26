from django.db import models
# from django.apps import apps


class video_class(models.Model):
    # video_id = models.IntegerField(primary_key=True)
    channel_id = models.IntegerField(null=True)
    video = models.FileField(upload_to='videous')
    length_of_video = models.IntegerField()
    url = models.URLField()
    thumb_image = models.ImageField(upload_to='thumb_image')
    like = models.IntegerField(default=0)
    dislike = models.IntegerField(default=0)
    description = models.CharField(max_length=200)
    tags = models.CharField(max_length=200,null=True)
    playlist = models.CharField(max_length=100,null=True)
    title = models.CharField(max_length=100)
    uploaded_on = models.DateTimeField(auto_now_add=True)
    is_downloadable = models.BooleanField(default=False)
    is_sharable = models.BooleanField(default=False)

    def __str__(self):
        return self.title

# PlayList