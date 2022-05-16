from django.urls import path, include
from .views import *

# app_name = 'account'

urlpatterns = [
    path('auth/', include('drf_social_oauth2.urls', namespace='drf')),
    path('signup/', sign_up, name='signup'),
    path('dashboard/', user_details, name='dashboard'),
    path('user-details/<int:pk>/', user_details, name='user-details'),
    path('update-profile/', update_profile, name='update-profile'),
    path('update-password/', update_password, name='update-password'),
    path('password-reset-request/', resetPasswordRequest,
         name='password-reser-request'),
    path('password-reset-check/<uid64>/<token>/', resetPasswordCheck,
         name='password-reset-check'),
    path('password-reset-confirm/', resetPasswordComplete,
         name='password-reset-confirm'),
]
