# Generated by Django 4.2 on 2023-04-26 01:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payapp', '0006_remove_request_destination_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='destination_username',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_request', to=settings.AUTH_USER_MODEL),
        ),
    ]