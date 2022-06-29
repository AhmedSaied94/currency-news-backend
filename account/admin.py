from django.contrib import admin
from account.models import *
from django.utils.html import format_html
from django.urls import reverse



# Register your models here.
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'fullname', 'email', 'home_currency', 'country', 'get_favorites')

    list_filter = ('join_date', 'is_staff', 'is_active', 'home_currency', 'country')

    search_fields = ('username__startswith', 'fullname__startswith', 'email__startwith')


    def get_favorites(self, obj):
        return format_html('<a href="{}{}/change/">{}</a>', reverse("admin:currency_userfavorite_changelist"), obj.favorites.id, obj.favorites.__str__())
    get_favorites.short_description = 'favorites'

    fieldsets = (
        ['Personal Details', {'fields': [
            'email', 'username', 'fullname', 'profile_pic']}],
        ['Area info', {'fields': ['country','home_currency']}],
        ['Status', {'fields': ['is_active', 'is_staff', 'is_superuser']}],
        ['Dates', {'fields': ['join_date', 'last_login']}],
        ['Permissions', {'fields': ['groups', 'user_permissions']}]
    )
