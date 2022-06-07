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

admin.site.register(DayValues)
admin.site.register(DayValuesLowHigh)
admin.site.register(Paragraph)
admin.site.register(AssetsType)
admin.site.register(NewsAsset)
