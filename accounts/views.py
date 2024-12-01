from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, View
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.views import (
    PasswordChangeView, 
    LoginView as BaseLoginView,
    LogoutView as BaseLogoutView
)
from django.contrib.auth import update_session_auth_hash, authenticate, login, logout
import logging
from django.db import models
from decimal import Decimal
from django.db.models import Sum
from django.conf import settings

# Local imports
from .models import User, Profile  # Removed Budget import
from .forms import UserCreationForm, UserUpdateForm, CustomPasswordChangeForm, UserRegistrationForm, ProfileEditForm, UserProfileForm
from website.models import Record  # Import the Record model instead of Transaction

logger = logging.getLogger(__name__)

class SuperAdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.can_manage_users

class SuperUserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

class UserListView(LoginRequiredMixin, SuperUserRequiredMixin, ListView):
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users = self.get_queryset()
        context.update({
            'total_users': users.count(),
            'active_users': users.filter(is_active=True).count(),
            'admin_users': users.filter(is_superuser=True).count(),
        })
        return context

class UserCreateView(LoginRequiredMixin, SuperUserRequiredMixin, CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')

    def form_valid(self, form):
        messages.success(self.request, 'User created successfully.')
        return super().form_valid(form)

class UserUpdateView(LoginRequiredMixin, SuperUserRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')

    def form_valid(self, form):
        messages.success(self.request, 'User updated successfully.')
        return super().form_valid(form)

class UserDeleteView(LoginRequiredMixin, SuperUserRequiredMixin, DeleteView):
    model = User
    template_name = 'accounts/user_confirm_delete.html'
    success_url = reverse_lazy('accounts:user_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'User deleted successfully.')
        return super().delete(request, *args, **kwargs)

class UserPasswordChangeView(LoginRequiredMixin, SuperUserRequiredMixin, View):
    template_name = 'accounts/user_password_change.html'
    success_url = reverse_lazy('accounts:user_list')

    def get_user(self):
        return get_object_or_404(User, pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        user = self.get_user()
        form = CustomPasswordChangeForm(user=user)
        return render(request, self.template_name, {'form': form, 'object': user})

    def post(self, request, *args, **kwargs):
        user = self.get_user()
        form = CustomPasswordChangeForm(user=user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Password changed successfully.')
            return redirect(self.success_url)
        return render(request, self.template_name, {'form': form, 'object': user})

class RegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        # Calculate profile completion
        required_fields = ['email', 'department', 'phone']
        completed_fields = sum(1 for field in required_fields if getattr(request.user, field))
        completion_percentage = (completed_fields / len(required_fields)) * 100

        # Get user's records statistics
        user_records = Record.objects.filter(created_by=request.user)
        context = {
            'completion_percentage': completion_percentage,
            'total_records': user_records.count(),
            'pending_approvals': user_records.filter(status='pending').count(),
            'approved_records': user_records.filter(status='approved').count(),
        }
        return render(request, 'accounts/profile.html', context)

class ProfileEditView(LoginRequiredMixin, UpdateView):
    template_name = 'accounts/profile_edit.html'
    form_class = UserProfileForm
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        """Return the current user's profile"""
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)

class LoginView(BaseLoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        next_url = self.request.GET.get('next') or self.request.POST.get('next')
        return next_url if next_url else reverse_lazy('website:dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hide_navbar'] = True
        context['next'] = self.request.GET.get('next') or self.request.POST.get('next')
        return context

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        next_url = self.request.POST.get('next')
        
        user = authenticate(self.request, username=username, password=password)
        if user is not None:
            # Check if user has 2FA enabled
            if user.totpdevice_set.filter(confirmed=True).exists():
                # Store user info and next URL in session for 2FA verification
                self.request.session['temp_user_id'] = user.id
                if next_url:
                    self.request.session['next_url'] = next_url
                return redirect('accounts:verify_2fa_login')
            else:
                # No 2FA, proceed with normal login
                login(self.request, user)
                return redirect(self.get_success_url())
        else:
            form.add_error(None, 'Invalid username or password')
            return self.form_invalid(form)

    def form_invalid(self, form):
        logger.error(f"Form errors: {form.errors}")
        return super().form_invalid(form)

    def dispatch(self, request, *args, **kwargs):
        if self.redirect_authenticated_user and self.request.user.is_authenticated:
            redirect_to = self.get_success_url()
            if redirect_to == self.request.path:
                raise ValueError(
                    "Redirection loop for authenticated user detected. Check that "
                    "your LOGIN_REDIRECT_URL doesn't point to a login page."
                )
            return redirect(redirect_to)
        return super().dispatch(request, *args, **kwargs)

class LogoutView(BaseLogoutView):
    next_page = 'accounts:login'

def verify_2fa_login(request):
    """Verify 2FA code during login"""
    # Check if we have a user in the session
    if 'temp_user_id' not in request.session:
        messages.error(request, 'Please log in first.')
        return redirect('accounts:login')

    if request.method == 'POST':
        code = request.POST.get('code')
        user_id = request.session.get('temp_user_id')
        
        try:
            user = User.objects.get(id=user_id)
            device = user.totpdevice_set.filter(confirmed=True).first()
            
            if device and device.verify_token(code):
                # Clear temporary session data
                next_url = request.session.pop('next_url', None)
                del request.session['temp_user_id']
                
                # Log the user in
                login(request, user)
                messages.success(request, 'Successfully authenticated with 2FA.')
                
                # Redirect to next URL if available, otherwise to dashboard
                return redirect(next_url if next_url else 'website:dashboard')
            else:
                messages.error(request, 'Invalid verification code.')
        except User.DoesNotExist:
            messages.error(request, 'Authentication failed. Please try logging in again.')
            return redirect('accounts:login')
    
    return render(request, 'accounts/verify_2fa_login.html')

# Rest of your views remain the same...
