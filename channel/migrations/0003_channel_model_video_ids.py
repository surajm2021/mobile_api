# Generated by Django 3.0 on 2019-12-26 08:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0006_auto_20191226_1316'),
        ('channel', '0002_auto_20191226_1316'),
    ]

    operations = [
        migrations.AddField(
            model_name='channel_model',
            name='video_ids',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='video.video_class'),
        ),
    ]