# Generated by Django 3.1.1 on 2020-10-29 19:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('manage_app', '0010_auto_20201024_1652'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceTrapModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trap_data', models.CharField(default=None, max_length=200, null=True)),
                ('device_model', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='manage_app.devicemodel')),
                ('user', models.ForeignKey(default=None, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
