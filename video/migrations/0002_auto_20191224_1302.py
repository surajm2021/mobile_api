# Generated by Django 3.0 on 2019-12-24 07:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='video_class',
            name='id',
        ),
        migrations.AlterField(
            model_name='video_class',
            name='channel_id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='video_class',
            name='dislike',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='video_class',
            name='is_downloadable',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='video_class',
            name='is_sharable',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='video_class',
            name='like',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='video_class',
            name='playlist',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
