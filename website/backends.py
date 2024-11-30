from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.cache import cache

User = get_user_model()

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Check for failed login attempts
            ip = request.META.get('REMOTE_ADDR')
            failed_attempts = cache.get(f'failed_login_{ip}', 0)
            if failed_attempts >= 5:
                return None

            # Try to fetch the user
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
            
            # Check password and active status
            if user.check_password(password) and self.user_can_authenticate(user):
                # Reset failed attempts on successful login
                cache.delete(f'failed_login_{ip}')
                return user
            else:
                # Increment failed attempts
                cache.set(f'failed_login_{ip}', failed_attempts + 1, 300)  # 5 minutes timeout
                return None
                
        except User.DoesNotExist:
            return None 