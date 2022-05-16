import imp
from msilib.schema import Class
from rest_framework import serializers
from currency.models import *
from account.api.v1.serializers import UserSerializer


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
            'content',
            'date',
            'comments',
        ]

    def get_comments(self, obj):
        return CommentSerialzer(
            instance=obj.comments.all(),
            many=True
        ).data


class ComparisonDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ComparisonDetails
        fields = '__all__'


class ComparisonSerializer(serializers.ModelSerializer):
    normal_currencies = serializers.SerializerMethodField()

    class Meta:
        model = Comparison
        fields = [
            'base_currency',
            'date',
            'normal_currencies'
        ]

    def get_normal_currencies(self, obj):
        return ComparisonDetailsSerializer(
            instance=obj.normal_curency.all(),
            many=True
        ).data


class CurrencySerializer(serializers.ModelSerializer):
    currency_type = serializers.SerializerMethodField()
    news = serializers.SerializerMethodField()
    comparisons = serializers.SerializerMethodField()

    class Meta:
        model = Currency
        fields = [
            'id',
            'name',
            'currency_type',
            'sympol',
            'news',
            'comparisons',
        ]

    def get_currency_type(self, obj):
        return TypeSerializer(
            instance=obj.currency_type
        ).data

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

    def get_comparisons(self, obj):
        return ComparisonSerializer(
            instance=obj.comparisons.all(),
            many=True
        ).data


class WalletSerializer(serializers.ModelSerializer):

    class Meta:
        model = Wallet
        fields = '__all__'


class CurrencyDetailsSerializer(serializers.ModelSerializer):

    currency = NewRepresent()
    value = serializers.SerializerMethodField()

    class Meta:
        model = CurrencyDetails
        fields = [
            'currency',
            'amount',
            'value',
        ]

    def get_value(self, obj):
        home_currency = obj.wallet.user.home_currency
        base_value = ComparisonDetails.objects.filter(
            normal_currency=home_currency,
            comparison__base_currency=obj.currency
        ).first().value

        return obj.amount * base_value
