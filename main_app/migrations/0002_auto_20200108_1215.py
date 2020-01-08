# Generated by Django 3.0 on 2020-01-08 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='admin',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='app_id',
            field=models.CharField(default=1, max_length=20, verbose_name='app_id'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='channel_id',
            field=models.IntegerField(null=True, verbose_name='channel_id'),
        ),
        migrations.AddField(
            model_name='user',
            name='dislikes',
            field=models.CharField(max_length=255, null=True, verbose_name='dislikes'),
        ),
        migrations.AddField(
            model_name='user',
            name='email',
            field=models.CharField(default=1, max_length=20, unique=True, verbose_name='email'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='is_staff',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='is_verify',
            field=models.BooleanField(default=False, verbose_name='is_verify'),
        ),
        migrations.AddField(
            model_name='user',
            name='likes',
            field=models.CharField(max_length=255, null=True, verbose_name='likes'),
        ),
        migrations.AddField(
            model_name='user',
            name='phone',
            field=models.CharField(default=1, max_length=20, unique=True, verbose_name='phone'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='tags',
            field=models.CharField(default=1, max_length=20, verbose_name='tags'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='username',
            field=models.CharField(default=1, max_length=20, unique=True, verbose_name='username'),
            preserve_default=False,
        ),
    ]