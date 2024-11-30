from django.contrib.auth.mixins import LoginRequiredMixin
from .models import UserActivity

class ActivityTrackingMixin:
    def log_activity(self, activity_type, description, record=None):
        UserActivity.objects.create(
            user=self.request.user,
            activity_type=activity_type,
            description=description,
            record=record,
            ip_address=self.request.META.get('REMOTE_ADDR')
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        if hasattr(self, 'activity_type') and hasattr(self, 'activity_description'):
            self.log_activity(
                self.activity_type,
                self.activity_description,
                getattr(self, 'object', None)
            )
        return response 