import os
import django
from celery import Celery
from django.conf import settings
from currency.tasks import add

os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'
# django.setup()

# Create default Celery app
app = Celery()

# namespace='CELERY' means all celery-related configuration keys
# should be uppercased and have a `CELERY_` prefix in Django settings.
# https://docs.celeryproject.org/en/stable/userguide/configuration.html
app.config_from_object("django.conf:settings", namespace="CELERY")

# When we use the following in Django, it loads all the <appname>.tasks
# files and registers any tasks it finds in them. We can import the
# tasks files some other way if we prefer.
app.autodiscover_tasks(settings.INSTALLED_APPS)