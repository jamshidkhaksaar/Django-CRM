from django.core.cache import cache
from django.http import JsonResponse
from datetime import datetime, timedelta

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit = 100  # requests per minute
        self.window = 60  # seconds

    def __call__(self, request):
        if request.path.startswith('/api/'):
            ip = request.META.get('REMOTE_ADDR')
            key = f'rate_limit_{ip}'
            
            # Get current requests count
            requests = cache.get(key, [])
            now = datetime.now()
            
            # Remove old requests
            requests = [req for req in requests 
                       if req > now - timedelta(seconds=self.window)]
            
            if len(requests) >= self.rate_limit:
                return JsonResponse({
                    'error': 'Rate limit exceeded'
                }, status=429)
            
            requests.append(now)
            cache.set(key, requests, self.window)

        return self.get_response(request) 