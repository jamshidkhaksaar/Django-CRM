from django.shortcuts import render, redirect
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from website.models import CustomUser
from .forms import UserCreationForm, UserUpdateForm, CustomPasswordChangeForm
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView, LoginView
from django.contrib.auth import update_session_auth_hash
import logging
from django.db import models
from .models import Budget
from django.contrib.auth import authenticate, login
from website.decorators import user_type_required
from website.models import Transaction, Record

logger = logging.getLogger(__name__)

class SuperAdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.can_manage_users

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
@user_type_required('superuser', 'data_entry', 'deputy_director', 'executive_director', 'chief_executive')
def dashboard(request):
    user = request.user
    context = {
        'user_type': user.get_user_type_display(),
        'total_transactions': Transaction.objects.count(),
        'can_manage_users': user.can_manage_users(),
        'can_approve_records': user.can_approve_records(),
        'can_edit_records': user.can_edit_record(),
        'can_delete_records': user.can_delete_record(),
    }
    
    # Add role-specific dashboard data
    if user.user_type == 'data_entry':
        context.update({
            'my_records': Record.objects.filter(created_by=user).count(),
            'pending_records': Record.objects.filter(created_by=user, approval_status__startswith='pending').count(),
        })
    elif user.user_type in ['deputy_director', 'executive_director', 'chief_executive']:
        status_mapping = {
            'deputy_director': 'pending_deputy',
            'executive_director': 'pending_executive',
            'chief_executive': 'pending_chief'
        }
        context.update({
            'pending_approvals': Record.objects.filter(
                approval_status=status_mapping[user.user_type]
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

class BudgetListView(LoginRequiredMixin, ListView):
    model = Budget
    template_name = 'accounts/budget_list.html'
    context_object_name = 'budgets'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_budget'] = Budget.objects.aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        return context

class BudgetCreateView(LoginRequiredMixin, CreateView):
    model = Budget
    template_name = 'accounts/budget_form.html'
    fields = ['name', 'amount', 'currency', 'start_date', 'end_date', 
              'period', 'category', 'notes']

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    success_url = reverse_lazy('home')
    redirect_authenticated_user = True

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back {username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'login.html')
