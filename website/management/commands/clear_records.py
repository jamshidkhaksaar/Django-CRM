from django.core.management.base import BaseCommand
from website.models import Record

class Command(BaseCommand):
    help = 'Clear all records while preserving users and database structure'

    def handle(self, *args, **kwargs):
        Record.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted all records')) 