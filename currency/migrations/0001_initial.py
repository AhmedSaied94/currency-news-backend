# Generated by Django 3.2.13 on 2022-05-15 16:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Comparison',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(verbose_name=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('sympol', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name_plural': 'Currencies',
            },
        ),
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('base_currency', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='UserFavorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currencies', models.ManyToManyField(to='currency.Currency')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('date', models.DateTimeField(verbose_name=django.utils.timezone.now)),
                ('base_currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='base_news', to='currency.currency')),
                ('normal_currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='normal_news', to='currency.currency')),
            ],
            options={
                'verbose_name_plural': 'News',
            },
        ),
        migrations.AddField(
            model_name='currency',
            name='currency_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='paper_currency', to='currency.type'),
        ),
        migrations.CreateModel(
            name='ComparisonDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField()),
                ('comparison', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='currency.comparison')),
                ('normal_currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='currency.currency')),
            ],
            options={
                'verbose_name_plural': 'Comparison Details',
            },
        ),
        migrations.AddField(
            model_name='comparison',
            name='base_currency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comparisons', to='currency.currency'),
        ),
        migrations.AddField(
            model_name='comparison',
            name='normal_currencies',
            field=models.ManyToManyField(through='currency.ComparisonDetails', to='currency.Currency'),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('date', models.DateTimeField(verbose_name=django.utils.timezone.now)),
                ('news', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Comments', to='currency.news')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]