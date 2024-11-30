from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Notification, Record
from .forms import AddRecordForm

def notification_processor(request):
    """Context processor for notifications with caching"""
    if not request.user.is_authenticated:
        return {}

    try:
        # Cache key unique to user
        cache_key = f'user_{request.user.id}_notifications'
        cache_key_count = f'user_{request.user.id}_unread_count'

        # Try to get cached notifications
        notifications = cache.get(cache_key)
        unread_count = cache.get(cache_key_count)

        if notifications is None or unread_count is None:
            # Get notifications with efficient querying
            all_notifications = (Notification.objects
                           .filter(user=request.user)
                           .select_related('record')  # Prefetch related record data
                           .order_by('-created_at'))

            # Get recent notifications for dropdown
            notifications = list(all_notifications[:5])
            
            # Get unread count
            unread_count = all_notifications.filter(is_read=False).count()

            # Cache the results for 5 minutes
            cache.set(cache_key, notifications, 300)
            cache.set(cache_key_count, unread_count, 300)

        return {
            'notifications': notifications,
            'unread_count': unread_count
        }
    except Exception as e:
        # Log the error properly
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Error in notification_processor: {str(e)}')
        return {
            'notifications': [],
            'unread_count': 0
        }

# Rest of your context processors...