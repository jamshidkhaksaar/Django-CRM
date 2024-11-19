from .models import Notification, CustomUser

def notification_processor(request):
    if request.user.is_authenticated:
        notifications_queryset = Notification.objects.filter(user=request.user)
        return {
            'recent_notifications': notifications_queryset.order_by('-created_at')[:5],
            'unread_notifications_count': notifications_queryset.filter(is_read=False).count()
        }
    return {}

def user_permissions(request):
    if request.user.is_authenticated:
        user_type = request.user.user_type
        status_to_approve = {
            'deputy_director': 'pending_deputy',
            'executive_director': 'pending_executive',
            'chief_executive': 'pending_chief'
        }.get(user_type)
        
        return {
            'status_to_approve': status_to_approve,
            'can_approve': user_type in ['deputy_director', 'executive_director', 'chief_executive'],
            'can_edit': user_type in ['superadmin', 'data_entry']
        }
    return {} 