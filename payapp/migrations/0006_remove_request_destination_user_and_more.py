# Generated by Django 4.2 on 2023-04-26 00:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payapp', '0005_request'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='request',
            name='destination_user',
        ),
        migrations.AddField(
            model_name='request',
            name='destination_username',
            field=models.CharField(default=1, max_length=30),
            preserve_default=False,
        ),
    ]
