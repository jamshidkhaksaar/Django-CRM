from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

def validate_auth_model():
    """Validate AUTH_USER_MODEL setting"""
    if not hasattr(settings, 'AUTH_USER_MODEL'):
        raise ImproperlyConfigured('AUTH_USER_MODEL must be set')
    if settings.AUTH_USER_MODEL != 'accounts.CustomUser':
        raise ImproperlyConfigured(
            f'AUTH_USER_MODEL must be accounts.CustomUser, got {settings.AUTH_USER_MODEL}'
        )