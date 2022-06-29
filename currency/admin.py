from django.contrib import admin
from .models import *
from django.urls import reverse
from django.utils.html import format_html, format_html_join
# Register your models here.

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'ar_name', 'sympol', 'country', 'currency_type', 'open_time', 'close_time')
    list_filter = ('open_time', 'close_time', 'currency_type')
    search_fields = ('name__startswith', 'sympol__startswith')

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('header', 'get_base_currency', 'get_normal_currency', 'date')
    list_filter = ('normal_currency', 'base_currency__currency_type', 'date')
    search_fields = ('base_currency__name__startswith', 'base_currency__sympol__startswith', 'normal_currency__name__startswith', 'normal_currency__sympol__startswith')

    def get_base_currency(self, obj):
        return format_html('<a href="{}{}/change/">{}</a>', reverse('admin:currency_currency_changelist'), obj.base_currency.id, obj.base_currency.name)
    get_base_currency.short_description = 'base_currency'
    def get_normal_currency(self, obj):
        return format_html('<a href="{}{}/change/">{}</a>', reverse('admin:currency_currency_changelist'), obj.normal_currency.id, obj.normal_currency.name)
    get_normal_currency.short_description = 'normal_currency'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('content', 'get_user', 'get_news', 'date')
    list_filter = ('user', 'news__base_currency__currency_type', 'date')

    def get_user(self, obj):
        return format_html('<a href="{}{}/change/">{}</a>', reverse('admin:account_userprofile_changelist'), obj.user.id, obj.user.username)
    get_user.short_description = 'user'

    def get_news(self, obj):
        return format_html('<a href="{}{}/change/">{}</a>', reverse('admin:currency_news_changelist'), obj.news.id, obj.news.header)
    get_news.short_description = 'news'

@admin.register(Comparison)
class ComparisonAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'get_base_currency', 'date')
    list_filter = ('base_currency', 'date')
    search_fields = ('base_currency__name__startswith', 'base_currency__sympol__startswith')

    def get_base_currency(self, obj):
        return format_html('<a href="{}{}/change/">{}</a>', reverse('admin:currency_currency_changelist'), obj.base_currency.id, obj.base_currency.name)
    get_base_currency.short_description = 'base_currency'

@admin.register(ComparisonDetails)
class ComparisonDetailsAdmin(admin.ModelAdmin):
    list_display = ( 'get_base_currency', 'get_normal_currency', 'get_bye_value', 'open_price', 'close_price', 'get_date')
    list_filter = ('comparison__base_currency','normal_currency', 'open_price', 'close_price', 'comparison__date')
    search_fields = ('normal_currency__name__startswith', 'normal_currency__sympol__startswith')

    def get_base_currency(self, obj):
        return format_html('<a href="{}{}/change/">{}</a>', reverse('admin:currency_currency_changelist'), obj.comparison.base_currency.id, obj.comparison.base_currency.name)
    get_base_currency.short_description = 'base_currency'

    def get_normal_currency(self, obj):
        return format_html('<a href="{}{}/change/">{}</a>', reverse('admin:currency_currency_changelist'), obj.normal_currency.id, obj.normal_currency.name)
    get_normal_currency.short_description = 'normal_currency'

    def get_date(self, obj):
        return obj.comparison.date
    get_date.short_description = 'time'

    def get_bye_value(self, obj):
        return str(round(obj.bye_value, 2)) + ' ' + obj.normal_currency.sympol
    get_bye_value.short_description = 'bye value'

@admin.register(UserFavorite)
class UserFavoriteAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'get_user', 'favorites')
    search_fields = ['user__name__startswith']
    def get_user(self, obj):
        return format_html('<a href="{}{}/change/">{}</a>', reverse('admin:account_userprofile_changelist'), obj.user.id, obj.user.username)
    get_user.short_description = 'user'

    def favorites(self, obj):
        return format_html_join(', ', '<a href="{}{}/change/">{}</a>', ((reverse('admin:currency_currency_changelist'), cur.id, cur.name) for cur in obj.currencies.all()))


@admin.register(DayValues)
class DayValuesAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'get_base_currency', 'date')
    list_filter = ('base_currency', 'date')
    search_fields = ('base_currency__name__startswith', 'base_currency__sympol__startswith')

    def get_base_currency(self, obj):
        return format_html('<a href="{}{}/change/">{}</a>', reverse('admin:currency_currency_changelist'), obj.base_currency.id, obj.base_currency.name)
    get_base_currency.short_description = 'base_currency'

@admin.register(DayValuesLowHigh)
class DayValuesLowHighAdmin(admin.ModelAdmin):
    list_display = ( 'get_base_currency', 'get_normal_currency', 'get_low_value', 'get_high_value', 'get_date')
    list_filter = ('day_values__base_currency','normal_currency', 'day_values__date')
    search_fields = ('normal_currency__name__startswith', 'normal_currency__sympol__startswith')

    def get_base_currency(self, obj):
        return format_html('<a href="{}{}/change/">{}</a>', reverse('admin:currency_currency_changelist'), obj.day_values.base_currency.id, obj.day_values.base_currency.name)
    get_base_currency.short_description = 'base_currency'

    def get_normal_currency(self, obj):
        return format_html('<a href="{}{}/change/">{}</a>', reverse('admin:currency_currency_changelist'), obj.normal_currency.id, obj.normal_currency.name)
    get_normal_currency.short_description = 'normal_currency'

    def get_date(self, obj):
        return obj.day_values.date
    get_date.short_description = 'time'

    def get_low_value(self, obj):
        return str(round(obj.low_value, 2)) + ' ' + obj.normal_currency.sympol
    get_low_value.short_description = 'low value'

    def get_high_value(self, obj):
        return str(round(obj.high_value, 2)) + ' ' + obj.normal_currency.sympol
    get_high_value.short_description = 'high value'

@admin.register(NewsAsset)
class NewsAssetAdmin(admin.ModelAdmin):
    list_display = ( 'asset', 'get_asset_type')
    list_filter = ('asset_type',)

    def get_asset_type(self, obj):
        return format_html('<a href="{}{}/change/">{}</a>', reverse('admin:currency_assetstype_changelist'), obj.asset_type.id, obj.asset_type.asset_type)
    get_asset_type.short_description = 'asset type'


admin.site.register(Type)
admin.site.register(Paragraph)
admin.site.register(AssetsType)
