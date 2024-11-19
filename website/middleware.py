from django.utils.deprecation import MiddlewareMixin
from .models import Notification

class NotificationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            request.notifications = Notification.objects.filter(
                user=request.user,
                is_read=False
            ).order_by('-created_at')[:5]
            request.unread_count = request.notifications.count() 