# Generated by Django 3.2.13 on 2022-05-15 16:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_auto_20220515_1624'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wallet',
            name='currencies',
        ),
        migrations.RemoveField(
            model_name='wallet',
            name='user',
        ),
        migrations.DeleteModel(
            name='CurrencyDetails',
        ),
        migrations.DeleteModel(
            name='Wallet',
        ),
    ]
