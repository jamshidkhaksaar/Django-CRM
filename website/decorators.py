from django.http import HttpResponseForbidden
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import get_user_model

User = get_user_model()

def user_type_required(*allowed_types):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'You must be logged in to access this page.')
                return redirect('accounts:login')
            
            if not hasattr(request.user, 'user_type') or request.user.user_type not in allowed_types:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('core:home')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def admin_required(view_func):
    return user_type_required('admin')(view_func)

def staff_required(view_func):
    return user_type_required('admin', 'staff')(view_func)

def data_entry_required(view_func):
    return user_type_required('admin', 'data_entry')(view_func)

def approver_required(view_func):
    return user_type_required('admin', 'deputy_director', 'executive_director', 'chief_executive')(view_func)

def record_permission_required(view_func):
    """Decorator to check record permissions"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
            
        record_id = kwargs.get('pk')
        if record_id:
            from .models import Record
            record = get_object_or_404(Record, pk=record_id)
            user = request.user
            
            # Check if user has permission to access the record
            if user.user_type == 'admin':
                return view_func(request, *args, **kwargs)
            elif user.user_type == 'data_entry':
                if user == record.created_by:
                    return view_func(request, *args, **kwargs)
            elif user.user_type in ['deputy_director', 'executive_director', 'chief_executive']:
                if record.status == 'pending':
                    return view_func(request, *args, **kwargs)
            
            raise PermissionDenied("You don't have permission to access this record.")
                
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
