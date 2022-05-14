from django.urls import path, include

# app_name = 'account'

urlpatterns = [
    path('auth/', include('drf_social_oauth2.urls', namespace='drf')),
]
