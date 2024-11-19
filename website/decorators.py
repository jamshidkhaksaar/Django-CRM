from django.http import HttpResponseForbidden
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from .models import CustomUser, Record

def user_type_required(*allowed_types):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                if request.user.user_type == 'superuser' or request.user.user_type in allowed_types:
                    return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("You do not have permission to access this page.")
        return _wrapped_view
    return decorator

def record_permission_required(view_func):
    """Decorator to check record permissions"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('login'))
            
        record_id = kwargs.get('pk')
        if record_id:
            record = get_object_or_404(Record, pk=record_id)
            user = request.user
            
            # Check if user has permission to access the record
            if user.user_type == 'superuser':
                return view_func(request, *args, **kwargs)
            elif user.user_type == 'data_entry':
                if user == record.created_by:
                    return view_func(request, *args, **kwargs)
            elif user.user_type in ['deputy_director', 'executive_director', 'chief_executive']:
                if record.approval_status == f'pending_{user.user_type.split("_")[0]}':
                    return view_func(request, *args, **kwargs)
            
            raise PermissionDenied
                
        return view_func(request, *args, **kwargs)
    return wrapper

def user_permission_required(permission_type):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return redirect('login')
                
            if permission_type == 'approve_records':
                if not user.can_approve_records():
                    raise PermissionDenied
            elif permission_type == 'manage_users':
                if not user.can_manage_users():
                    raise PermissionDenied
                    
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
