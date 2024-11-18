from django.http import HttpResponseForbidden
from functools import wraps
from .models import CustomUser

def user_type_required(user_type):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                if isinstance(request.user, CustomUser) and (request.user.user_type == user_type or request.user.user_type == 'superadmin'):
                    return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("You do not have permission to access this page.")
        return _wrapped_view
    return decorator
