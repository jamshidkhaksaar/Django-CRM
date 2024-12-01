from django.shortcuts import redirect
from django.urls import reverse
from django_otp.plugins.otp_totp.models import TOTPDevice

class Require2FAMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        if request.user.is_authenticated:
            device = TOTPDevice.objects.filter(user=request.user, confirmed=True).first()
            
            if device and not request.session.get('2fa_verified'):
                if request.path not in [
                    reverse('accounts:verify_2fa'),
                    reverse('accounts:logout'),
                    reverse('accounts:setup_2fa')
                ]:
                    request.session['next'] = request.path
                    return redirect('accounts:verify_2fa')
        
        return self.get_response(request) 