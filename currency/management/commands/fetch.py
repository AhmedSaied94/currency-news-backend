from django.core.management.base import BaseCommand

from currency.tasks import start_scheduler


class Command(BaseCommand):
    help = "Starts the scheduler"

    def handle(self, *args, **options):
        try:
            start_scheduler()
            self.stdout.write(self.style.SUCCESS("Scheduler started"))
        except Exception as e:
            print(e)
            self.stdout.write(self.style.ERROR(str(e)))
