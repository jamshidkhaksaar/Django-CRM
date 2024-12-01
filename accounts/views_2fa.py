from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.util import random_hex
import qrcode
import qrcode.image.svg
from io import BytesIO
import base64

@login_required
def setup_2fa(request):
    """View for setting up 2FA"""
    # Check if user already has 2FA device
    if TOTPDevice.objects.filter(user=request.user, confirmed=True).exists():
        messages.warning(request, '2FA is already enabled for your account.')
        return redirect('accounts:profile')

    # Create new TOTP device
    device = TOTPDevice.objects.create(
        user=request.user,
        name=f"{request.user.username}'s device",
        confirmed=False,
        key=random_hex()
    )

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(device.config_url)
    qr.make(fit=True)

    # Create QR code image
    img_buffer = BytesIO()
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(img_buffer, format='PNG')
    qr_code = base64.b64encode(img_buffer.getvalue()).decode()

    context = {
        'qr_code': qr_code,
        'secret_key': device.key,
    }
    return render(request, 'accounts/2fa_setup.html', context)

@login_required
def verify_2fa(request):
    """View for verifying 2FA setup"""
    if request.method == 'POST':
        token = request.POST.get('token')
        device = TOTPDevice.objects.get(user=request.user, confirmed=False)
        
        if device.verify_token(token):
            device.confirmed = True
            device.save()
            messages.success(request, '2FA has been successfully enabled.')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Invalid verification code.')
    
    return render(request, 'accounts/2fa_verify.html')

@login_required
def disable_2fa(request):
    if request.method == 'POST':
        if request.user.totpdevice_set.exists():
            request.user.totpdevice_set.all().delete()
            messages.success(request, 'Two-factor authentication has been disabled.')
        return redirect('accounts:profile')
    return redirect('accounts:profile')