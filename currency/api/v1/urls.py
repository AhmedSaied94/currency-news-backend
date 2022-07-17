from django.urls import path
from .views import *


urlpatterns = [
    path('currency-details/<str:sympol>/',
         currency_details, name='currency-details'),
    path('all-currencies/<str:type>/', get_all_currencies, name='all-currencies'),
    path('all-sympols/', get_all_sympols, name='all-sympols'),
    path('news-details/<str:type>/', get_news, name='all-news'),
    path('news-details/<str:filter>/<int:pk>/<str:head>/',
         get_news, name='news-details'),
    path('handle-likes/', handle_likes, name='handle-likes'),
    path('handle-comments/', handle_comments, name='handle-comments'),
    path('handle-favorites/', handle_favorites, name='handle-favorites'),
    path('calculator/', calculator, name='calculator'),
    path('search/', search_cur, name='search')

]
