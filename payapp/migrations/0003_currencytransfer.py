# Generated by Django 4.2 on 2023-04-23 22:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payapp', '0002_rename_money_currency_value_currency_currency'),
    ]

    operations = [
        migrations.CreateModel(
            name='CurrencyTransfer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('origin_account', models.CharField(max_length=50)),
                ('destination_account', models.CharField(max_length=50)),
                ('value', models.DecimalField(decimal_places=2, max_digits=16)),
            ],
        ),
    ]
