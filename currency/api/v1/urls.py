from django.urls import path
from .views import *


urlpatterns = [
    path('currency-details/<str:sympol>/',
         currency_details, name='currency-details'),
    path('all-currencies/<str:type>/', get_all_currencies, name='all-currencies'),
    path('all-sympols/', get_all_sympols, name='all-sympols')
]
