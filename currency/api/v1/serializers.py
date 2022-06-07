from locale import currency
from multiprocessing import context
from turtle import home
from rest_framework import serializers
from currency.models import *
from datetime import date, datetime, timedelta
from django_countries.serializers import CountryFieldMixin


class NewRepresent(serializers.StringRelatedField):
    def to_internal_value(self, value):
        return value


class TypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Type
        fields = '__all__'


class CommentSerialzer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = '__all__'


class NewsSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = [
            'header',
            'sub_header',
            'body1',
            'body2',
            'date',
            'comments',
        ]

    def get_comments(self, obj):
        return CommentSerialzer(
            instance=obj.comments.all(),
            many=True
        ).data


class ComparisonDetailsSerializer(serializers.ModelSerializer):
    normal_currency = NewRepresent()

    class Meta:
        model = ComparisonDetails
        fields = [
            'normal_currency',
            'bye_value',
        ]


class ComparisonSerializer(serializers.ModelSerializer):
    normal_currencies = serializers.SerializerMethodField()

    class Meta:
        model = Comparison
        fields = ['normal_currencies']

    def get_normal_currencies(self, obj):
        for i in obj.normal_currencies.all():
            lista = []
            for j in Currency.objects.all():
                if i == j:
                    continue
                lista.append({
                    "name": j.name,
                    "value": j.get_exchange_value(i)
                })
            return lista


class CurrencySerializer(CountryFieldMixin, serializers.ModelSerializer):
    currency_type = NewRepresent()
    news = serializers.SerializerMethodField()
    # comparisons = serializers.SerializerMethodField()
    home_value = serializers.SerializerMethodField()
    last7_low_high = serializers.SerializerMethodField()
    day_low_high = serializers.SerializerMethodField()
    open_price = serializers.SerializerMethodField()
    close_price = serializers.SerializerMethodField()
    last7graph = serializers.SerializerMethodField()

    class Meta:
        model = Currency
        fields = [
            'id',
            'name',
            'currency_type',
            'sympol',
            'country',
            'news',
            'home_value',
            'last7_low_high',
            'day_low_high',
            'open_price',
            'close_price',
            'last7graph',
            # 'comparisons',
        ]

    # def get_currency_type(self, obj):
    #     return TypeSerializer(
    #         instance=obj.currency_type
    #     ).data

    def get_news(self, obj):
        if obj.currency_type.base_currency:
            news = NewsSerializer(
                instance=obj.base_news.all(),
                many=True
            ).data
        else:
            news = NewsSerializer(
                instance=obj.normal_news.all(),
                many=True
            ).data
        return news

    def get_home_value(self, obj):
        if obj.currency_type.base_currency == True:
            home = self.context['home']
            if obj == home:
                return 1
            else:
                return str(ComparisonDetails.objects.filter(comparison__base_currency=obj, normal_currency=home).order_by('-comparison__date').first().bye_value) + ' ' + home.sympol
        base_cur = Currency.objects.get(sympol='USD')
        return str(1 / ComparisonDetails.objects.filter(comparison__base_currency=base_cur, normal_currency=obj).order_by('-comparison__date').bye_value) + ' ' + base_cur.sympol

        # return obj.get_exchange_value(base)

    def get_last7_low_high(self, obj):
        today = datetime.today()
        base = obj if obj.currency_type.base_currency else Currency.objects.get(
            sympol='USD')
        home = self.context['home'] if obj.currency_type.base_currency == True else obj
        qs = DayValuesLowHigh.objects.filter(
            day_values__date__range=(today-timedelta(days=7), today),
            day_values__base_currency=base,
            normal_currency=home
        )
        if obj.currency_type.base_currency:
            last7low_high = {
                'low': str(qs.order_by('low_value').first().low_value) + f" {home.sympol}",
                'high': str(qs.order_by('-high_value').first().high_value) + f" {home.sympol}"
            }
        else:
            last7low_high = {
                'low': str(1 / qs.order_by('-high_value').first().high_value) + f' {base.sympol}',
                'high': str(1 / qs.order_by('low_value').first().low_value) + f' {base.sympol}'
            }
        return last7low_high

    def get_day_low_high(self, obj):
        base = obj if obj.currency_type.base_currency == True else Currency.objects.get(
            sympol='USD')
        home = self.context['home'] if obj.currency_type.base_currency == True else obj
        day_low_high = DayValuesLowHigh.objects.get(
            day_values__date=datetime.today()-timedelta(days=1),
            day_values__base_currency=base,
            normal_currency=home
        )
        if obj.currency_type.base_currency:
            day_low_high_values = {
                "low": str(day_low_high.low_value) + f' {home.sympol}',
                "high": str(day_low_high.high_value) + f' {home.sympol}'
            }
        else:
            day_low_high_values = {
                "low": str(1 / day_low_high.high_value) + f' {base.sympol}',
                "high": str(1 / day_low_high.low_value) + f' {base.sympol}'
            }
        return day_low_high_values

    def get_open_price(self, obj):
        base = obj if obj.currency_type.base_currency == True else Currency.objects.get(
            sympol='USD')
        home = self.context['home'] if obj.currency_type.base_currency == True else obj
        price = ComparisonDetails.objects.filter(
            comparison__date__date=datetime.today() - timedelta(days=1),
            comparison__base_currency=base,
            normal_currency=home,
            open_price=True
        ).first().bye_value
        return str(price) + f' {home.sympol}' if obj.currency_type.base_currency else str(1/price) + f' {base.sympol}'

    def get_close_price(self, obj):
        base = obj if obj.currency_type.base_currency == True else Currency.objects.get(
            sympol='USD')
        home = self.context['home'] if obj.currency_type.base_currency == True else obj
        price = ComparisonDetails.objects.filter(
            comparison__date__date=datetime.today() - timedelta(days=1),
            comparison__base_currency=base,
            normal_currency=home,
            close_price=True
        ).first().bye_value
        return str(price) + f' {home.sympol}' if obj.currency_type.base_currency else str(1/price) + f' {base.sympol}'

    def get_last7graph(self, obj):
        lista = []
        base = obj if obj.currency_type.base_currency == True else Currency.objects.get(
            sympol='USD')
        home = self.context['home'] if obj.currency_type.base_currency == True else obj
        qs = ComparisonDetails.objects.filter(
            comparison__base_currency=base,
            comparison__date__range=(
                datetime.today()-timedelta(days=8), datetime.today()-timedelta(days=1)),
            normal_currency=home,
            close_price=True
        ).order_by('comparison__date')
        for ins in qs:
            if obj.currency_type.base_currency:
                lista.append(ins.bye_value)
            else:
                lista.append(1/ins.bye_value)
        return lista

    # def get_comparisons(self, obj):
    #     # return ComparisonSerializer(
    #     #     instance=obj.comparisons.all(),
    #     #     many=True,
    #     # ).data
    #     lista = []
    #     if obj.currency_type.base_currency:
    #         for com in obj.comparisons.all().first().comparison_details.all():
    #             lista.append({
    #                 'value': f'{com.bye_value} {com.normal_currency.sympol}',
    #                 'normal_currency': com.normal_currency.name
    #             })
    #         # return ComparisonDetailsSerializer(
    #         #     instance=lista,
    #         #     many=True
    #         # ).data
    #         return lista
    #     else:
    #         return ''


class AllCurrencySerializer(CountryFieldMixin, serializers.ModelSerializer):
    currency_type = NewRepresent()
    # news = serializers.SerializerMethodField()
    home_value = serializers.SerializerMethodField()
    last7_low_high = serializers.SerializerMethodField()
    day_low_high = serializers.SerializerMethodField()
    open_price = serializers.SerializerMethodField()
    close_price = serializers.SerializerMethodField()
    last7graph = serializers.SerializerMethodField()

    class Meta:
        model = Currency
        fields = [
            'id',
            'name',
            'currency_type',
            'sympol',
            'country',
            # 'news',
            'home_value',
            'last7_low_high',
            'day_low_high',
            'open_price',
            'close_price',
            'last7graph',
        ]

    # def get_news(self, obj):
    #     if obj.currency_type.base_currency:
    #         news = NewsSerializer(
    #             instance=obj.base_news.all(),
    #             many=True
    #         ).data
    #     else:
    #         news = NewsSerializer(
    #             instance=obj.normal_news.all(),
    #             many=True
    #         ).data
    #     return news

    def get_home_value(self, obj):
        home = self.context['home']
        if obj == home:
            return 1
        else:
            value = home.comparisons_details.filter(
                comparison__base_currency=obj).order_by('-comparison__date').first().bye_value
            return value

    def get_last7_low_high(self, obj):
        today = datetime.today()
        home = self.context['home']
        qs = DayValuesLowHigh.objects.filter(
            day_values__date__range=(today-timedelta(days=7), today),
            day_values__base_currency=obj,
            normal_currency=home
        )
        last7low_high = {
            'low': qs.order_by('low_value').first().low_value,
            'high': qs.order_by('-high_value').first().high_value
        }
        return last7low_high

    def get_day_low_high(self, obj):
        home = self.context['home']
        day_low_high = DayValuesLowHigh.objects.get(
            day_values__date=datetime.today()-timedelta(days=1),
            day_values__base_currency=obj,
            normal_currency=home
        )
        return {
            "low": day_low_high.low_value,
            "high": day_low_high.high_value
        }

    def get_open_price(self, obj):
        home = self.context['home']
        return ComparisonDetails.objects.filter(
            comparison__date__date=datetime.today() - timedelta(days=1),
            comparison__base_currency=obj,
            normal_currency=home,
            open_price=True
        ).first().bye_value

    def get_close_price(self, obj):
        home = self.context['home']
        return ComparisonDetails.objects.filter(
            comparison__date__date=datetime.today() - timedelta(days=1),
            comparison__base_currency=obj,
            normal_currency=home,
            close_price=True
        ).first().bye_value

    def get_last7graph(self, obj):
        lista = []
        qs = ComparisonDetails.objects.filter(
            comparison__base_currency=obj,
            comparison__date__range=(
                datetime.today()-timedelta(days=8), datetime.today()-timedelta(days=1)),
            normal_currency=self.context['home'],
            close_price=True
        ).order_by('comparison__date')
        for ins in qs:
            lista.append(ins.bye_value)
        return lista


class CurrencySympolsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Currency
        fields = [
            'name',
            'sympol',
        ]
