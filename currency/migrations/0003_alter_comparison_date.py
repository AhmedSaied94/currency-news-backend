# Generated by Django 3.2.13 on 2022-05-15 16:35

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('currency', '0002_auto_20220515_1633'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comparison',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
