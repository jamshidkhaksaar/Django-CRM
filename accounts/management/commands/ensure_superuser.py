from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()

class Command(BaseCommand):
    help = 'Ensures that a superuser exists'

    def handle(self, *args, **options):
        try:
            if not User.objects.filter(is_superuser=True).exists():
                User.objects.create_superuser(
                    username='admin',
                    email='admin@example.com',
                    password='admin123'
                )
                self.stdout.write(self.style.SUCCESS('Superuser created successfully'))
            else:
                self.stdout.write(self.style.SUCCESS('Superuser already exists'))
        except IntegrityError:
            self.stdout.write(self.style.ERROR('An error occurred while creating the superuser')) 