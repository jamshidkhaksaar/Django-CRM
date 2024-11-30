from django.shortcuts import render, redirect
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
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
from .forms import UserCreationForm, UserUpdateForm, CustomPasswordChangeForm, UserRegistrationForm, ProfileEditForm

logger = logging.getLogger(__name__)

class SuperAdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.can_manage_users

class UserListView(LoginRequiredMixin, SuperAdminRequiredMixin, ListView):
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'

class CreateUserView(LoginRequiredMixin, SuperAdminRequiredMixin, CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('user_list')

    def form_valid(self, form):
        try:
            logger.info("="*50)
            logger.info("Creating new user:")
            logger.info(f"Username: {form.cleaned_data.get('username')}")
            logger.info(f"User type: {form.cleaned_data.get('user_type')}")
            
            user = form.save()
            user.is_active = True
            user.is_staff = True
            user.save(update_fields=['is_active', 'is_staff'])
            
            logger.info("User saved to database:")
            logger.info(f"Username: {user.username}")
            logger.info(f"Is active: {user.is_active}")
            logger.info(f"Is staff: {user.is_staff}")
            logger.info("="*50)
            
            messages.success(self.request, f'User {user.username} created successfully')
            return redirect(self.success_url)
            
        except Exception as e:
            logger.error("="*50)
            logger.error(f"Error creating user: {str(e)}")
            logger.error("="*50)
            return self.form_invalid(form)

class RegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

class ProfileView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'accounts/profile.html'
    
    def get_object(self):
        return self.request.user.profile

class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileEditForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')

class LoginView(BaseLoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('website:dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hide_navbar'] = True
        return context

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        
        user = authenticate(self.request, username=username, password=password)
        if user is not None:
            login(self.request, user)
            next_url = self.request.GET.get('next')
            if next_url and next_url != '/':
                return redirect(next_url)
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

# Rest of your views remain the same...
