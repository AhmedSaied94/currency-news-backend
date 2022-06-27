"""currency_news URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from currency.views import iframe, bases_to_arabic, frame_data

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/account/', include('account.api.v1.urls')),
    path('api/', include('currency.api.v1.urls')),
    path('iframe/', iframe, name='iframe'),
    path('bases_frame/', bases_to_arabic, name='bases_frame'),
    path('frame-data/', frame_data, name='frame-data')

]


if settings.DEBUG:
    urlpatterns += path('__debug__/', include('debug_toolbar.urls')),
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
