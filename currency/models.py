from django.db import models
from django.conf import settings
from django.utils import timezone
# Create your models here.


class Type(models.Model):
    name = models.CharField(max_length=100,)
    base_currency = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Currency(models.Model):
    currency_type = models.ForeignKey(
        'Type', related_name='paper_currency', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    sympol = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Currencies'


class News(models.Model):
    content = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    base_currency = models.ForeignKey(
        'Currency', related_name='base_news', on_delete=models.CASCADE)
    normal_currency = models.ForeignKey(
        'Currency', related_name='normal_news', on_delete=models.CASCADE)

    def __str__(self):
        return f'New news for {self.base_currency} and {self.normal_currency}'

    class Meta:
        verbose_name_plural = 'News'


class Comment(models.Model):
    content = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='comments', on_delete=models.CASCADE)
    news = models.ForeignKey(
        'News', related_name='Comments', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username} commented on an news for {self.news.first_currency} and {self.news.second_currency}'


class Comparison(models.Model):
    base_currency = models.ForeignKey(
        'Currency', related_name='comparisons', on_delete=models.CASCADE)
    normal_currencies = models.ManyToManyField(
        'Currency', through='ComparisonDetails')
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'update for {self.base_currency} price'


class ComparisonDetails(models.Model):
    normal_currency = models.ForeignKey('Currency', on_delete=models.CASCADE)
    comparison = models.ForeignKey('Comparison', on_delete=models.CASCADE)
    value = models.FloatField()

    def str(self):
        return f'{self.comparison.base_currency} is now = {self.amount} {self.normal_currency}'

    class Meta:
        verbose_name_plural = 'Comparisons Normal Currencies Details'


class UserFavorite(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='favorites', on_delete=models.CASCADE)
    currencies = models.ManyToManyField('Currency')

    def __str__(self):
        return f'{self.user.username} favorites'


class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='wallet', on_delete=models.CASCADE)
    currencies = models.ManyToManyField('Currency', through='CurrencyDetails')

    def __str__(self):
        return f'{self.user.username} wallet'


class CurrencyDetails(models.Model):
    currency = models.ForeignKey('Currency', on_delete=models.CASCADE)
    amount = models.FloatField()
    wallet = models.ForeignKey('Wallet', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.wallet.user.username} have {self.amount} {self.currency.name}'

    class Meta:
        verbose_name_plural = 'Wallets Currencies Details'
