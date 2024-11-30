from django.http import JsonResponse
from django.conf import settings
import jwt
from datetime import datetime, timedelta

class APIAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/api/'):
            # Check for API token
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'error': 'No token provided'}, status=401)

            try:
                # Verify token
                payload = jwt.decode(
                    token.split(' ')[1], 
                    settings.SECRET_KEY, 
                    algorithms=['HS256']
                )
                request.user_id = payload.get('user_id')
            except jwt.ExpiredSignatureError:
                return JsonResponse({'error': 'Token expired'}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'error': 'Invalid token'}, status=401)

        response = self.get_response(request)
        return response

def generate_token(user):
    """Generate JWT token for API authentication"""
    payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256') 