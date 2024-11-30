# website/management/commands/migrate_users.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import CustomUser

class Command(BaseCommand):
    help = 'Migrate existing users to CustomUser model'

    def handle(self, *args, **kwargs):
        for user in User.objects.all():
            if not CustomUser.objects.filter(username=user.username).exists():
                custom_user = CustomUser.objects.create(
                    username=user.username,
                    email=user.email,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    is_staff=user.is_staff,
                    is_superuser=user.is_superuser,
                    is_active=user.is_active,
                    user_type='superadmin',  # Set admin users as superadmin
                    department='Administration',
                    phone='',
                )
                # Copy the password hash directly
                custom_user.password = user.password
                custom_user.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully migrated user: {user.username}'))
            else:
                self.stdout.write(self.style.WARNING(f'User {user.username} already exists in CustomUser. Skipping.'))