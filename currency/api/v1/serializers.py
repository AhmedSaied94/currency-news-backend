from locale import currency
from multiprocessing import context
from turtle import home
from rest_framework import serializers
from currency.models import *
from datetime import date, datetime, timedelta
from django_countries.serializers import CountryFieldMixin
from googletrans import Translator
from django.contrib.auth import get_user_model
translator = Translator()
User = get_user_model()


def calc_values(value, carat):
    return round(value/31.1/24*carat, 2)


class UserData(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['profile_pic', 'fullname']


class NewRepresent(serializers.StringRelatedField):
    def to_internal_value(self, value):
        return value


class TypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Type
        fields = '__all__'


class CommentSerialzer(serializers.ModelSerializer):
    userdata = serializers.SerializerMethodField()
    customDate = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'content', 'date', 'user',
                  'news', 'userdata', 'customDate']

    def get_userdata(self, obj):
        return UserData(instance=obj.user).data

    def get_customDate(self, obj):
        return obj.date.strftime("%A %-d %B, %Y")


class NewsSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()
    date = serializers.DateTimeField("%A %-d %B, %Y")
    ar_date = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()
    close_value = serializers.SerializerMethodField()
    cur_name = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    profit_margin = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = [
            'id',
            'header',
            'sub_header',
            'body1',
            'body2',
            'date',
            'comments',
            'value',
            'cur_name',
            'ar_date',
            'close_value',
            'likes',
            'profit_margin'
        ]


    def get_profit_margin(self, obj):

        margin = ProfitMarginDetails.objects.filter(
        profit_margin__base_currency=obj.base_currency,
        normal_currency=obj.normal_currency
        )
        return margin.first().value if margin.exists() else None

    def get_comments(self, obj):
        return CommentSerialzer(
            instance=obj.comments.all(),
            many=True
        ).data

    def get_likes(self, obj):
        if hasattr(obj, 'likes') and self.context:
            return obj.likes.user.all().count()
        else:
            return 0

    def get_ar_date(self, obj):
        if self.context:
            return translator.translate(obj.date.strftime("%A %-d %B, %Y"), src='en', dest='ar').text

    def get_value(self, obj):
        if not self.context:
            return None
        if obj.base_currency.name == 'Gold' or obj.base_currency.name == 'Silver':

            value = ComparisonDetails.objects.get(
                comparison__date=obj.date,
                comparison__base_currency=obj.base_currency,
                normal_currency=obj.normal_currency
            ).bye_value

            values = {
                '12': calc_values(value, 12),
                '14': calc_values(value, 14),
                '18': calc_values(value, 18),
                '21': calc_values(value, 21),
                '24': calc_values(value, 24),
                'ingot 5': calc_values(value, 24)*5,
                'ingot 20': calc_values(value, 24)*20,
                'ingot 1k': calc_values(value, 24)*1000,
                'ounce': round(value, 2)
            }if obj.base_currency.name == 'Gold' else {
                '999': round(value/31.1, 2),
                '925': round(value/33.6, 2),
                '888': round(value/38.85, 2),
                'ounce': round(value, 2)
            }
            return values

    def get_close_value(self, obj):
        if not self.context:
            return None
        if obj.base_currency.name == 'Gold' or obj.base_currency.name == 'Silver':
            print(obj.base_currency, obj.normal_currency)
            value = ComparisonDetails.objects.filter(
                comparison__date__date=obj.date.date()-timedelta(days=1),
                comparison__base_currency=obj.base_currency,
                normal_currency=obj.normal_currency,
                close_price=True
            ).first().bye_value
            values = {
                '12': calc_values(value, 12),
                '14': calc_values(value, 14),
                '18': calc_values(value, 18),
                '21': calc_values(value, 21),
                '24': calc_values(value, 24),
                'ingot 5': calc_values(value, 24)*5,
                'ingot 20': calc_values(value, 24)*20,
                'ingot 1k': calc_values(value, 24)*1000,
                'ounce': round(value, 2)
            }if obj.base_currency.name == 'Gold' else {
                '999': round(value/31.1, 2),
                '925': round(value/33.6, 2),
                '888': round(value/38.85, 2),
                'ounce': round(value, 2)
            }
            return values

    def get_cur_name(self, obj):
        if self.context:
            return {
                'normal': obj.normal_currency.ar_name,
                'base': obj.base_currency.ar_name,
                'country': translator.translate(obj.normal_currency.country.name, src='en', dest='ar').text
            }


class ComparisonDetailsSerializer(serializers.ModelSerializer):
    normal_currency = serializers.SerializerMethodField()
    h24 = serializers.SerializerMethodField()
    sell_value = serializers.SerializerMethodField()

    class Meta:
        model = ComparisonDetails
        fields = [
            'normal_currency',
            'bye_value',
            'h24',
            'sell_value'
        ]

    def get_normal_currency(self, obj):
        return {
            "name": obj.normal_currency.name,
            "sympol": obj.normal_currency.sympol,
        }

    def get_sell_value(self, obj):

        margin = ProfitMarginDetails.objects.filter(
        profit_margin__base_currency=obj.comparison.base_currency,
        normal_currency=obj.normal_currency
        )
        return obj.bye_value + margin.first().value if margin.exists() else obj.bye_value

    def get_h24(self, obj):
        close = ComparisonDetails.objects.filter(
            comparison__base_currency=obj.comparison.base_currency,
            normal_currency=obj.normal_currency,
            close_price=True
        ).order_by('-comparison__date').first().bye_value
        print((obj.bye_value-close)/close*100)
        return round((obj.bye_value-close)/close*100, 3)


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
        qs = obj.normal_news.all() if not obj.currency_type.base_currency else obj.base_news.all()
        news = NewsSerializer(
            instance=qs.order_by('-date'),
            many=True
        ).data
        return news

    def get_home_value(self, obj):
        if obj.currency_type.base_currency == True:
            home = self.context['home']
            if obj == home:
                return 1
            else:
                return str(round(ComparisonDetails.objects.filter(comparison__base_currency=obj, normal_currency=home).order_by('-comparison__date').first().bye_value, 3)) + ' ' + home.sympol
        else:
            # lista = {}
            # for cur in Currency.objects.filter(currency_type__name='Base_Currency'):
            #     value = ComparisonDetails.objects.filter(
            #         comparison__base_currency=cur, normal_currency=obj).order_by('-comparison__date').first().bye_value
            #     lista[cur.sympol] = f'{round(1/value, 3)} {cur.sympol}'
            # return lista
            value = ComparisonDetails.objects.filter(
                comparison__base_currency=self.context['base'],
                normal_currency=obj
            ).order_by('-comparison__date').first().bye_value
            return str(round(value, 2)) + f' {obj.sympol}'
        # return obj.get_exchange_value(base)

    def get_last7_low_high(self, obj):
        today = datetime.today()
        base = obj if obj.currency_type.base_currency else self.context['base']
        home = obj if not obj.currency_type.base_currency else self.context['home']
        qs = DayValuesLowHigh.objects.filter(
            day_values__date__range=(today-timedelta(days=22), today),
            day_values__base_currency=base,
            normal_currency=home
        )
        # if obj.currency_type.base_currency:
        last7low_high = {
            'low': str(round(qs.order_by('low_value').first().low_value, 3)) + f" {home.sympol}",
            'high': str(round(qs.order_by('-high_value').first().high_value, 3)) + f" {home.sympol}"
        }
        # else:
        #     last7low_high = {
        #         'low': str(round(qs.order_by('-high_value').first().high_value, 3)) + f' {base.sympol}',
        #         'high': str(round(qs.order_by('low_value').first().low_value, 3)) + f' {base.sympol}'
        #     }
        return last7low_high

    def get_day_low_high(self, obj):
        base = obj if obj.currency_type.base_currency else self.context['base']
        home = obj if not obj.currency_type.base_currency else self.context['home']
        day_low_high = DayValuesLowHigh.objects.get(
            day_values__date=datetime.today()-timedelta(days=22),
            day_values__base_currency=base,
            normal_currency=home
        )
        # if obj.currency_type.base_currency:
        day_low_high_values = {
            "low": str(round(day_low_high.low_value, 3)) + f' {home.sympol}',
            "high": str(round(day_low_high.high_value, 3)) + f' {home.sympol}'
        }
        # else:
        #     day_low_high_values = {
        #         "low": str(round(1 / day_low_high.high_value, 3)) + f' {base.sympol}',
        #         "high": str(round(1 / day_low_high.low_value, 3)) + f' {base.sympol}'
        #     }
        return day_low_high_values

    def get_open_price(self, obj):
        base = obj if obj.currency_type.base_currency else self.context['base']
        home = obj if not obj.currency_type.base_currency else self.context['home']
        price = ComparisonDetails.objects.filter(
            comparison__date__date=datetime.today() - timedelta(days=22),
            comparison__base_currency=base,
            normal_currency=home,
            open_price=True
        ).first().bye_value
        return str(round(price, 3)) + f' {home.sympol}'
        # if obj.currency_type.base_currency else str(round(1/price, 3)) + f' {base.sympol}'

    def get_close_price(self, obj):
        base = obj if obj.currency_type.base_currency else self.context['base']
        home = obj if not obj.currency_type.base_currency else self.context['home']
        price = ComparisonDetails.objects.filter(
            comparison__date__date=datetime.today() - timedelta(days=22),
            comparison__base_currency=base,
            normal_currency=home,
            close_price=True
        ).first().bye_value
        return str(round(price, 3)) + f' {home.sympol}'
        # if obj.currency_type.base_currency else str(round(1/price, 3)) + f' {base.sympol}'

    def get_last7graph(self, obj):
        lista = []
        base = obj if obj.currency_type.base_currency else self.context['base']
        home = obj if not obj.currency_type.base_currency else self.context['home']
        qs = ComparisonDetails.objects.filter(
            comparison__base_currency=base,
            comparison__date__range=(
                datetime.today()-timedelta(days=22), datetime.today()-timedelta(days=1)),
            normal_currency=home,
            close_price=True
        ).order_by('comparison__date')
        for ins in qs:
            # if obj.currency_type.base_currency:
            lista.append(ins.bye_value)
            # else:
            #     lista.append(1/ins.bye_value)
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
    profit_margin = serializers.SerializerMethodField()

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
            'profit_margin',
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
            day_values__date__range=(today-timedelta(days=22), today),
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
            day_values__date=datetime.today()-timedelta(days=22),
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
            comparison__date__date=datetime.today() - timedelta(days=22),
            comparison__base_currency=obj,
            normal_currency=home,
            open_price=True
        ).first().bye_value

    def get_close_price(self, obj):
        home = self.context['home']
        return ComparisonDetails.objects.filter(
            comparison__date__date=datetime.today() - timedelta(days=22),
            comparison__base_currency=obj,
            normal_currency=home,
            close_price=True
        ).first().bye_value

    def get_last7graph(self, obj):
        lista = []
        qs = ComparisonDetails.objects.filter(
            comparison__base_currency=obj,
            comparison__date__range=(
                datetime.today()-timedelta(days=22), datetime.today()-timedelta(1)),
            normal_currency=self.context['home'],
            close_price=True
        ).order_by('comparison__date')
        for ins in qs:
            lista.append(ins.bye_value)
        return lista

    def get_profit_margin(self, obj):

        margin = ProfitMarginDetails.objects.filter(
        profit_margin__base_currency=obj,
        normal_currency=self.context['home']
        )
        return margin.first().value if margin.exists() else None



class CurrencySympolsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Currency
        fields = [
            'name',
            'sympol',
            'id'
        ]
