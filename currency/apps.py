from django.apps import AppConfig
import os


class CurrencyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "currency"

    # def ready(self):
    #     from . import tasks

    #     if os.environ.get("RUN_MAIN", None) != "true":
    #         tasks.start_scheduler()
