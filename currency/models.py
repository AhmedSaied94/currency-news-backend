from datetime import date
from datetime import time
from django.db import models
from django.conf import settings
from django.utils import timezone
from django_countries.fields import CountryField
# Create your models here.


class Type(models.Model):
    name = models.CharField(max_length=100,)
    base_currency = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Comparison(models.Model):
    base_currency = models.ForeignKey(
        'Currency', related_name='comparisons', on_delete=models.CASCADE)
    normal_currencies = models.ManyToManyField(
        'Currency', through='ComparisonDetails')
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'update for {self.base_currency} price'


class ComparisonDetails(models.Model):
    normal_currency = models.ForeignKey(
        'Currency', related_name='comparisons_details', on_delete=models.CASCADE)
    comparison = models.ForeignKey(
        'Comparison', related_name='comparison_details', on_delete=models.CASCADE)
    bye_value = models.FloatField()
    open_price = models.BooleanField(default=False)
    close_price = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.comparison.base_currency} is now = {self.bye_value} {self.normal_currency}'

    class Meta:
        verbose_name_plural = 'Comparisons Normal Currencies Details'


class DayValues(models.Model):
    date = models.DateField()
    base_currency = models.ForeignKey(
        'Currency', related_name='day_values_bases', on_delete=models.CASCADE)
    normal_currencies = models.ManyToManyField(
        'Currency', through='dayValuesLowHigh')

    def __str__(self):
        return f'Day values for {self.base_currency.name}'


class DayValuesLowHigh(models.Model):
    day_values = models.ForeignKey(
        'DayValues', related_name='day_values_low_high', on_delete=models.CASCADE)
    normal_currency = models.ForeignKey(
        'Currency', related_name='day_values_low_high', on_delete=models.CASCADE)
    low_value = models.FloatField()
    high_value = models.FloatField()

    def __str__(self):
        return f'Day low & high values between {self.normal_currency.name} and {self.day_values.base_currency.name}'


class ProfitMargin(models.Model):
    base_currency = models.OneToOneField(
        'Currency', related_name='profit_margin_bases', on_delete=models.CASCADE)
    normal_currencies = models.ManyToManyField(
        'Currency', through='ProfitMarginDetails')


class ProfitMarginDetails(models.Model):
    profit_margin = models.ForeignKey(
        'ProfitMargin', related_name='profit_margin_details', on_delete=models.CASCADE)
    normal_currency = models.OneToOneField(
        'Currency', related_name='profit_margin_details', on_delete=models.CASCADE)
    value = models.FloatField(null=True, blank=True)


class Currency(models.Model):
    currency_type = models.ForeignKey(
        'Type', related_name='paper_currency', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    sympol = models.CharField(max_length=100)
    open_time = models.TimeField(default=time(0, 5))
    close_time = models.TimeField(default=time(6, 0))
    country = CountryField(null=True)

    def __str__(self):
        return self.name

    def get_exchange_value(self, base):
        if self == base:
            return 1
        qs = ComparisonDetails.objects.filter(
            normal_currency=self.id,
            comparison__base_currency=base
        ).first()
        return qs.bye_value

    class Meta:
        verbose_name_plural = 'Currencies'


class News(models.Model):
    header = models.TextField()
    body1 = models.TextField()
    sub_header = models.TextField(null=True)
    body2 = models.TextField(null=True, blank=True)
    paragraphs = models.ForeignKey(
        'Paragraph', related_name='news', on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(default=timezone.now)
    base_currency = models.ForeignKey(
        'Currency', related_name='base_news', on_delete=models.CASCADE)
    normal_currency = models.ForeignKey(
        'Currency', related_name='normal_news', on_delete=models.CASCADE)

    def __str__(self):
        return self.header

    class Meta:
        verbose_name_plural = 'News'


class NewsAsset(models.Model):
    asset = models.CharField(max_length=100)
    asset_type = models.ForeignKey(
        'AssetsType', related_name='assets', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.asset} {self.asset_type.asset_type} asset"


class Paragraph(models.Model):
    p1 = models.TextField(null=True, blank=True)
    p2 = models.TextField(null=True, blank=True)
    currency = models.OneToOneField(
        'Currency', related_name='paraghraphs', on_delete=models.CASCADE)


class AssetsType(models.Model):
    asset_type = models.CharField(max_length=100)

    def __str__(self):
        return self.asset_type


class Comment(models.Model):
    content = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='comments', on_delete=models.CASCADE)
    news = models.ForeignKey(
        'News', related_name='comments', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username} commented on an news for {self.news.first_currency} and {self.news.second_currency}'


class UserFavorite(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='favorites', on_delete=models.CASCADE)
    currencies = models.ManyToManyField('Currency')

    def __str__(self):
        return f'{self.user.username} favorites'
