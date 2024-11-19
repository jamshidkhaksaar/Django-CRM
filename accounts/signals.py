from django.db.models.signals import post_save
from django.dispatch import receiver
from website.models import CustomUser
from .models import UserProfile

@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Create or update the user profile."""
    if created:
        UserProfile.objects.create(user=instance)
    else:
        # Get or create the profile if it doesn't exist
        profile, created = UserProfile.objects.get_or_create(user=instance)
        if not created:
            profile.save() 
        