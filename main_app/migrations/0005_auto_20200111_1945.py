# Generated by Django 3.0 on 2020-01-11 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0004_delete_employee'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='dislikes',
            field=models.CharField(max_length=255, null=True, verbose_name='dislikes'),
        ),
        migrations.AlterField(
            model_name='user',
            name='likes',
            field=models.CharField(max_length=255, null=True, verbose_name='likes'),
        ),
    ]
