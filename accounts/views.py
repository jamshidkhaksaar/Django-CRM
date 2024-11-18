from django.shortcuts import render, redirect
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from website.models import CustomUser
from .forms import UserCreationForm, UserUpdateForm, CustomPasswordChangeForm
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import update_session_auth_hash
import logging

logger = logging.getLogger(__name__)

class SuperAdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

class UserListView(LoginRequiredMixin, SuperAdminRequiredMixin, ListView):
    model = CustomUser
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'

class CreateUserView(LoginRequiredMixin, SuperAdminRequiredMixin, CreateView):
    model = CustomUser
    form_class = UserCreationForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('user_list')

    def form_valid(self, form):
        try:
            # Log form data before saving
            logger.info("="*50)
            logger.info("Creating new user:")
            logger.info(f"Username: {form.cleaned_data.get('username')}")
            logger.info(f"User type: {form.cleaned_data.get('user_type')}")
            
            # Let Django's form handle the user creation and password hashing
            user = form.save()
            
            # Set additional flags after save
            user.is_active = True
            user.is_staff = True
            user.save(update_fields=['is_active', 'is_staff'])
            
            # Log the final user state
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

class EditUserView(LoginRequiredMixin, SuperAdminRequiredMixin, UpdateView):
    model = CustomUser
    form_class = UserUpdateForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('user_list')

class DeleteUserView(LoginRequiredMixin, SuperAdminRequiredMixin, DeleteView):
    model = CustomUser
    template_name = 'accounts/user_confirm_delete.html'
    success_url = reverse_lazy('user_list')

@login_required
def dashboard(request):
    user = request.user
    context = {
        'user_type': user.get_user_type_display(),
        'total_transactions': Transaction.objects.count(),
    }
    
    if user.user_type == 'cashier':
        context.update({
            'my_transactions': Transaction.objects.filter(created_by=user).count(),
            'pending_transactions': Transaction.objects.filter(created_by=user, status='pending').count(),
        })
    else:
        status_to_check = {
            'deputy_director': 'pending',
            'executive_director': 'first_approval',
            'chief_executive': 'second_approval'
        }
        if user.user_type in status_to_check:
            context.update({
                'pending_approvals': Transaction.objects.filter(
                    status=status_to_check[user.user_type]
                ).count()
            })
    
    return render(request, 'accounts/dashboard.html', context)

class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('user_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Keep the user logged in after password change
        update_session_auth_hash(self.request, self.request.user)
        messages.success(self.request, 'Password updated successfully')
        return response
