# Generated by Django 3.1.1 on 2020-10-18 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manage_app', '0002_auto_20201015_1951'),
    ]

    operations = [
        migrations.AddField(
            model_name='devicemodel',
            name='system_image',
            field=models.CharField(default=None, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='devicemodel',
            name='system_type',
            field=models.CharField(default=None, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='devicemodel',
            name='system_version',
            field=models.CharField(default=None, max_length=50, null=True),
        ),
    ]
