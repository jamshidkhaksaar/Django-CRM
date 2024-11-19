from django.core.management.base import BaseCommand
from accounts.models import CustomUser
from website.models import UserProfile

class Command(BaseCommand):
    help = 'Creates UserProfile for users that do not have one'

    def handle(self, *args, **kwargs):
        users = CustomUser.objects.all()
        created_count = 0
        
        for user in users:
            profile, created = UserProfile.objects.get_or_create(user=user)
            if created:
                created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} user profiles'
            )
        ) 