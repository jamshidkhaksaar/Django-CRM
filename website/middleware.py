from django.core.cache import cache
from django.utils import timezone
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
import pytz

class OnlineUsersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            cache_key = f'user-online-{request.user.pk}'
            cache.set(cache_key, True, 300)
        
        response = self.get_response(request)
        return response 

class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            current_time = timezone.now()
            last_activity = request.session.get('last_activity')
            
            if last_activity:
                last_activity = pytz.UTC.localize(timezone.datetime.fromisoformat(last_activity))
                time_elapsed = (current_time - last_activity).total_seconds()
                
                if time_elapsed > 30 * 60:  # 30 minutes
                    logout(request)
                    messages.warning(request, 'Your session has expired. Please login again.')
                    return redirect('accounts:login')
            
            request.session['last_activity'] = current_time.isoformat()

        response = self.get_response(request)
        return response

class IPBlockerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.blocked_ips = set()
        self.failed_attempts = {}

    def __call__(self, request):
        ip = request.META.get('REMOTE_ADDR')
        
        if ip in self.blocked_ips:
            return HttpResponseForbidden('Your IP has been blocked due to too many failed attempts.')
        
        if request.path == '/accounts/login/' and request.method == 'POST':
            if not request.user.is_authenticated:
                self.failed_attempts[ip] = self.failed_attempts.get(ip, 0) + 1
                if self.failed_attempts[ip] >= 5:  # Block after 5 failed attempts
                    self.blocked_ips.add(ip)
                    return HttpResponseForbidden('Too many failed login attempts.')
            else:
                self.failed_attempts.pop(ip, None)
        
        response = self.get_response(request)
        return response 