from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Type)
admin.site.register(Currency)
admin.site.register(News)
admin.site.register(Comment)
admin.site.register(Comparison)
admin.site.register(ComparisonDetails)
admin.site.register(UserFavorite)
admin.site.register(Wallet)
admin.site.register(CurrencyDetails)
