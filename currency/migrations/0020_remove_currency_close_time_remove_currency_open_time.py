# Generated by Django 4.0.5 on 2022-06-05 18:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('currency', '0019_assetstype_rename_content_news_body1_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='currency',
            name='close_time',
        ),
        migrations.RemoveField(
            model_name='currency',
            name='open_time',
        ),
    ]
