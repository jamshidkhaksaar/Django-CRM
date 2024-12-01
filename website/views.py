from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import logout, authenticate, login
from django.shortcuts import redirect
from django.db.models import Sum
from decimal import Decimal
from django.contrib.auth import get_user_model
from .models import Record, UserSettings, RecordApproval, Notification, UserActivity, AdvancePayback
from django.views.generic import UpdateView, TemplateView, ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .forms import (
    AddRecordForm, 
    RecordForm, 
    UserForm, 
    UserEditForm, 
    UserPermissionsForm, 
    UserSettingsForm
)
from .mixins import ActivityTrackingMixin
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import CreateView, DeleteView
from django.utils import timezone
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from .utils import log_activity, get_client_ip
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

User = get_user_model()

@login_required(login_url='/accounts/login/')
def home(request):
    # Log activity with IP
    log_activity(
        request=request,
        activity_type='view_home',
        description='Viewed home page'
    )
    
    # Get all records
    all_records = Record.objects.all().order_by('-created_at')
    
    # Get records by type and status
    approved_records = all_records.filter(status='approved')
    balance_records = all_records.filter(transaction_type='balance')
    income_records = all_records.filter(transaction_type='income')
    expense_records = all_records.filter(transaction_type='expense')
    advance_records = all_records.filter(transaction_type='advance')
    payable_records = all_records.filter(transaction_type='payable')
    
    # Calculate totals from approved records only
    approved_balance = approved_records.filter(transaction_type='balance').aggregate(Sum('amount'))['amount__sum'] or 0
    total_income = approved_records.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expenses = approved_records.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    total_advances = approved_records.filter(transaction_type='advance').aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Calculate payables (only include unpaid ones since paid ones have been settled)
    total_payables = approved_records.filter(transaction_type='payable', is_paid=False).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Calculate outstanding amounts
    total_advance_paybacks = AdvancePayback.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    outstanding_advances = total_advances - total_advance_paybacks
    
    # Calculate total balance including all transactions
    total_balance = (
        approved_balance +  # Start with approved balance entries
        total_income +  # Add income
        total_payables +  # Add only unpaid payables (loans we still need to pay)
        -total_expenses -  # Subtract expenses
        outstanding_advances  # Subtract outstanding advances
    )
    
    # Get number of pending records
    pending_advances = advance_records.exclude(
        id__in=AdvancePayback.objects.filter(
            is_fully_paid=True
        ).values_list('advance_id', flat=True)
    ).count()
    
    pending_payables = payable_records.filter(is_paid=False).count()
    
    context = {
        'all_records': all_records,
        'balance_records': balance_records,
        'income_records': income_records,
        'expense_records': expense_records,
        'advance_records': advance_records,
        'payable_records': payable_records,
        'total_balance': total_balance,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'total_payables': total_payables,
        'outstanding_advances': outstanding_advances,
        'pending_advances': pending_advances,
        'pending_payables': pending_payables,
        'last_update': timezone.now(),
    }
    
    return render(request, 'home.html', context)

@login_required
def dashboard(request):
    # Log activity with IP
    log_activity(
        request=request,
        activity_type='view_dashboard',
        description='Viewed dashboard'
    )
    
    # Get approved records only
    approved_records = Record.objects.filter(status='approved')
    
    # Get total counts
    total_records = Record.objects.count()
    pending_records = Record.objects.filter(status='pending').count()
    approved_records_count = approved_records.count()
    rejected_records = Record.objects.filter(status='rejected').count()
    
    # Get financial totals
    total_income = approved_records.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    total_expenses = approved_records.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    total_balance = approved_records.filter(transaction_type='balance').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    total_advances = approved_records.filter(transaction_type='advance').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    total_advance_paybacks = AdvancePayback.objects.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    # Calculate outstanding advances
    outstanding_advances = total_advances - total_advance_paybacks
    
    # Calculate net profit
    net_profit = total_income - total_expenses
    
    # Calculate cash flow
    cash_flow = total_income - total_expenses - outstanding_advances
    
    # Calculate profit margin
    profit_margin = (net_profit / total_income * 100) if total_income > 0 else Decimal('0.00')
    
    # Calculate cash flow ratio
    cash_flow_ratio = (cash_flow / total_expenses) if total_expenses > 0 else Decimal('0.00')
    
    # Calculate advance recovery rate
    advance_recovery_rate = (total_advance_paybacks / total_advances * 100) if total_advances > 0 else Decimal('0.00')
    
    # Calculate operating efficiency
    total_transactions = total_income + total_expenses
    operating_efficiency = (net_profit / total_transactions * 100) if total_transactions > 0 else Decimal('0.00')
    
    # Get monthly data for charts
    today = timezone.now()
    last_12_months = [(today - timezone.timedelta(days=x*30)).strftime('%B %Y') for x in range(11, -1, -1)]
    monthly_income = []
    monthly_expenses = []
    
    for month in range(11, -1, -1):
        month_start = today.replace(day=1) - timezone.timedelta(days=month*30)
        month_end = (month_start + timezone.timedelta(days=32)).replace(day=1)
        
        month_income = approved_records.filter(
            transaction_type='income',
            created_at__gte=month_start,
            created_at__lt=month_end
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        month_expenses = approved_records.filter(
            transaction_type='expense',
            created_at__gte=month_start,
            created_at__lt=month_end
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        monthly_income.append(float(month_income))
        monthly_expenses.append(float(month_expenses))
    
    # Get high-value transactions (top 10 by amount)
    high_value_transactions = approved_records.order_by('-amount')[:10]
    
    # Calculate profit growth (compare with last month)
    current_month_profit = monthly_income[-1] - monthly_expenses[-1]
    last_month_profit = monthly_income[-2] - monthly_expenses[-2]
    profit_growth = ((current_month_profit - last_month_profit) / last_month_profit * 100) if last_month_profit != 0 else 0
    
    # Get pending amount
    pending_amount = Record.objects.filter(status='pending').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    context = {
        # Record counts
        'total_records': total_records,
        'pending_records': pending_records,
        'approved_records': approved_records_count,
        'rejected_records': rejected_records,
        'pending_count': pending_records,
        
        # Financial totals
        'total_income': total_income,
        'total_expenses': total_expenses,
        'total_balance': total_balance,
        'total_advances': total_advances,
        'outstanding_advances': outstanding_advances,
        'net_profit': net_profit,
        'cash_flow': cash_flow,
        'pending_amount': pending_amount,
        
        # Financial metrics
        'profit_margin': profit_margin,
        'cash_flow_ratio': cash_flow_ratio,
        'advance_recovery_rate': advance_recovery_rate,
        'operating_efficiency': operating_efficiency,
        'profit_growth': profit_growth,
        
        # Status indicators
        'profit_margin_status': 'Good' if profit_margin > 20 else 'Needs Improvement',
        'cash_flow_status': 'Positive' if cash_flow > 0 else 'Negative',
        'recovery_status': 'Good' if advance_recovery_rate > 80 else 'Needs Follow-up',
        'efficiency_status': 'Efficient' if operating_efficiency > 85 else 'Needs Optimization',
        
        # Chart data
        'monthly_labels': last_12_months,
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expenses,
        'advance_count': approved_records.filter(transaction_type='advance').exclude(
            id__in=AdvancePayback.objects.filter(is_fully_paid=True).values_list('advance_id', flat=True)
        ).count(),
        
        # Transactions
        'high_value_transactions': high_value_transactions,
    }
    
    return render(request, 'website/dashboard.html', context)

class LandingPageView(TemplateView):
    template_name = 'landing.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('website:home')
        return super().get(request, *args, **kwargs)

class UserSettingsView(ActivityTrackingMixin, LoginRequiredMixin, UpdateView):
    model = UserSettings
    form_class = UserSettingsForm
    template_name = 'website/user_settings.html'
    success_url = '/website/settings/'

    def get_object(self, queryset=None):
        return UserSettings.objects.get_or_create(user=self.request.user)[0]

    def form_valid(self, form):
        response = super().form_valid(form)
        # Log activity with IP
        log_activity(
            request=self.request,
            activity_type='update_settings',
            description='Updated user settings'
        )
        return response

class RecordListView(LoginRequiredMixin, ListView):
    model = Record
    template_name = 'website/record_list.html'
    context_object_name = 'records'
    paginate_by = 10

    def get_queryset(self):
        # Log activity with IP
        log_activity(
            request=self.request,
            activity_type='view_records',
            description='Viewed records list'
        )
        return Record.objects.all().order_by('-created_at')

class BalanceRecordListView(RecordListView):
    def get_queryset(self):
        return super().get_queryset().filter(transaction_type='balance')

class IncomeRecordListView(RecordListView):
    def get_queryset(self):
        return super().get_queryset().filter(transaction_type='income')

class ExpenseRecordListView(RecordListView):
    def get_queryset(self):
        return super().get_queryset().filter(transaction_type='expense')

class AdvanceRecordListView(RecordListView):
    def get_queryset(self):
        return super().get_queryset().filter(transaction_type='advance')

class PayableRecordListView(RecordListView):
    def get_queryset(self):
        return super().get_queryset().filter(transaction_type='payable')

class MyRecordListView(RecordListView):
    def get_queryset(self):
        return super().get_queryset().filter(created_by=self.request.user)

class ApprovedRecordListView(RecordListView):
    def get_queryset(self):
        return super().get_queryset().filter(status='approved')

class RejectedRecordListView(RecordListView):
    def get_queryset(self):
        return super().get_queryset().filter(status='rejected')

class PendingRecordListView(RecordListView):
    def get_queryset(self):
        return super().get_queryset().filter(status='pending')

@login_required
def record_detail(request, pk):
    """
    Display detailed information about a specific record.
    """
    record = get_object_or_404(Record, pk=pk)
    
    # Log activity with IP
    log_activity(
        request=request,
        activity_type='view_record_detail',
        description=f'Viewed record detail: {record.reference_number}',
        record=record
    )
    
    context = {
        'record': record,
    }
    return render(request, 'website/record_detail.html', context)

@login_required
def record_approval(request, pk):
    """Handle record approval/rejection process."""
    record = get_object_or_404(Record, pk=pk)
    
    if not record.can_approve(request.user):
        messages.error(request, "You don't have permission to approve this record at its current stage.")
        return redirect('website:record_detail', pk=pk)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        comments = request.POST.get('comments', '')
        
        if status in ['approved', 'rejected']:
            record.status = status
            record.save()
            
            # Create approval record
            RecordApproval.objects.create(
                record=record,
                user=request.user,
                approval_level=request.user.user_type,
                status=status,
                comments=comments
            )
            
            # Create notification for record creator
            Notification.objects.create(
                user=record.created_by,
                title=f'Record {status.title()}',
                message=f'Your record {record.reference_number} has been {status} by {request.user.get_full_name()}.',
                record=record
            )
            
            # Log user activity with IP address
            log_activity(
                request=request,
                activity_type='record_approve' if status == 'approved' else 'record_reject',
                description=f'{status.title()} record: {record.reference_number}',
                record=record
            )
            
            messages.success(request, f"Record has been {status}.")
            
    return redirect('website:record_detail', pk=pk)

@login_required
def forward_to_deputy(request, pk):
    """Forward a record from cashier to deputy director."""
    record = get_object_or_404(Record, pk=pk)
    
    if request.user.user_type != 'cashier' or record.forwarded_to_deputy:
        messages.error(request, "You don't have permission to forward this record.")
        return redirect('website:record_detail', pk=pk)
    
    if request.method == 'POST':
        comments = request.POST.get('comments', '')
        
        # Update record status
        record.status = 'pending_deputy'
        record.forwarded_to_deputy = True
        record.save()
        
        # Create approval record for cashier's review
        RecordApproval.objects.create(
            record=record,
            user=request.user,
            approval_level='cashier',
            status='forwarded',
            comments=comments
        )
        
        # Notify deputy directors
        deputy_directors = User.objects.filter(user_type='deputy_director')
        for deputy in deputy_directors:
            Notification.objects.create(
                user=deputy,
                title='New Record for Review',
                message=f'Record {record.reference_number} has been forwarded for your approval.',
                record=record
            )
        
        # Create user activity
        UserActivity.objects.create(
            user=request.user,
            activity_type='record_forward',
            description=f'Forwarded record {record.reference_number} to Deputy Director',
            record=record
        )
        
        messages.success(request, "Record has been forwarded to Deputy Director for approval.")
    
    return redirect('website:record_detail', pk=pk)

@login_required
def add_record(request):
    if request.method == 'POST':
        try:
            # Get form data
            transaction_type = request.POST.get('transaction_type')
            amount = request.POST.get('amount')
            date = request.POST.get('date')
            description = request.POST.get('description')
            balance_type = request.POST.get('balance_type')
            
            # Create record
            record = Record.objects.create(
                transaction_type=transaction_type,
                amount=amount,
                date=date,
                description=description,
                balance_type=balance_type,
                created_by=request.user,
                status='pending'
            )
            
            # Log activity with IP
            log_activity(
                request=request,
                activity_type='create_record',
                description=f'Created new {transaction_type} record: {record.reference_number}',
                record=record
            )
            
            print(f"Record saved successfully: {record.id}")
            
            # Create notification for staff users
            try:
                # Get all staff users except the current user
                staff_users = User.objects.filter(is_staff=True).exclude(id=request.user.id)
                
                for staff_user in staff_users:
                    Notification.objects.create(
                        user=staff_user,
                        title='New Record Added',
                        message=f'A new {transaction_type} record has been added by {request.user.get_full_name() or request.user.username}',
                        record=record,
                        notification_type='record_status'
                    )
                    
                # Also create a notification for superusers if they're not staff
                superusers = User.objects.filter(is_superuser=True, is_staff=False)
                for superuser in superusers:
                    Notification.objects.create(
                        user=superuser,
                        title='New Record Added',
                        message=f'A new {transaction_type} record has been added by {request.user.get_full_name() or request.user.username}',
                        record=record,
                        notification_type='record_status'
                    )
                    
            except Exception as e:
                print(f"Error creating notifications: {str(e)}")
            
            # Send WebSocket notification
            try:
                from channels.layers import get_channel_layer
                from asgiref.sync import async_to_sync
                
                channel_layer = get_channel_layer()
                notification_data = {
                    'type': 'notification',
                    'notification': {
                        'title': 'New Record Added',
                        'message': f'A new {transaction_type} record has been added by {request.user.get_full_name() or request.user.username}',
                        'record_id': record.id,
                        'notification_id': record.id
                    }
                }
                
                # Send to all staff users
                for user in staff_users:
                    async_to_sync(channel_layer.group_send)(
                        f'user_{user.id}_notifications',
                        notification_data
                    )
                
                # Send to superusers
                for user in superusers:
                    async_to_sync(channel_layer.group_send)(
                        f'user_{user.id}_notifications',
                        notification_data
                    )
                    
            except Exception as e:
                print(f"Error sending WebSocket notification: {str(e)}")
            
            return JsonResponse({
                'status': 'success', 
                'message': 'Record added successfully',
                'record_id': record.id
            })
            
        except Exception as e:
            print(f"Error saving record: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def edit_record(request, pk):
    """Handle editing of existing records."""
    record = get_object_or_404(Record, pk=pk)
    
    # Check if user has permission to edit
    if not request.user.can_edit_record():
        messages.error(request, "You don't have permission to edit records.")
        return redirect('website:record_detail', pk=pk)
    
    if request.method == 'POST':
        form = RecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, "Record updated successfully.")
            return redirect('website:record_detail', pk=pk)
    else:
        form = RecordForm(instance=record)
    
    return render(request, 'website/record_form.html', {
        'form': form,
        'title': 'Edit Record',
        'button_text': 'Update Record',
        'record': record
    })

@login_required
def notifications(request):
    """View for displaying all notifications"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_notifications = notifications.filter(is_read=False)
    
    context = {
        'notifications': notifications,
        'unread_count': unread_notifications.count(),
    }
    return render(request, 'website/notifications.html', context)

@login_required
def mark_notification_read(request, pk):
    """
    Mark a specific notification as read.
    """
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.read = True
    notification.save()
    
    # If this is an AJAX request, return JSON response
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    # If there's a next URL in query params, redirect there
    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
    
    # Otherwise redirect to notifications list
    return redirect('website:notifications')

@login_required
def mark_all_notifications_as_read(request):
    if request.method == 'POST':
        request.user.notifications.filter(is_read=False).update(is_read=True)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Display list of users. Only accessible by staff members.
    """
    model = User
    template_name = 'website/user_list.html'
    context_object_name = 'users'
    paginate_by = 10
    
    def test_func(self):
        """Only allow staff members to access this view."""
        return self.request.user.is_superuser and self.request.user.user_type == 'admin'
    
    def get_queryset(self):
        """Return all users ordered by date joined."""
        return self.model.objects.all().order_by('-date_joined')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'User List'
        return context

class UserCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    View for creating new users. Only accessible by staff members.
    """
    model = User
    form_class = UserForm
    template_name = 'website/user_form.html'
    success_url = reverse_lazy('website:user_list')
    
    def test_func(self):
        """Only allow staff members to access this view."""
        return self.request.user.is_superuser and self.request.user.user_type == 'admin'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "User created successfully.")
        return response

class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    View for updating existing users. Only accessible by staff members.
    """
    model = User
    form_class = UserEditForm
    template_name = 'website/user_form.html'
    success_url = reverse_lazy('website:user_list')
    
    def test_func(self):
        """Only allow staff members to access this view."""
        return self.request.user.is_superuser and self.request.user.user_type == 'admin'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit User: {self.object.username}'
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "User updated successfully.")
        return response

class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    View for deleting users. Only accessible by staff members.
    """
    model = User
    template_name = 'website/user_confirm_delete.html'
    success_url = reverse_lazy('website:user_list')
    
    def test_func(self):
        """
        Only allow staff members to access this view.
        Also prevent users from deleting themselves.
        """
        return (self.request.user.is_superuser and 
                self.request.user.user_type == 'admin' and
                self.request.user.pk != self.kwargs.get('pk'))
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "User deleted successfully.")
        return super().delete(request, *args, **kwargs)

class UserPermissionsView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    View for managing user permissions. Only accessible by staff members.
    """
    model = User
    form_class = UserPermissionsForm
    template_name = 'website/user_permissions.html'
    success_url = reverse_lazy('website:user_list')
    
    def test_func(self):
        """Only allow staff members to access this view."""
        return self.request.user.is_superuser and self.request.user.user_type == 'admin'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Permissions: {self.object.username}'
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "User permissions updated successfully.")
        return response

class UserActivityListView(LoginRequiredMixin, ListView):
    """
    Display list of user activities.
    """
    model = UserActivity
    template_name = 'website/activity_list.html'
    context_object_name = 'activities'
    paginate_by = 20
    
    def get_queryset(self):
        """Return all activities with proper ordering and filtering."""
        queryset = UserActivity.objects.all().select_related('user', 'record')
        
        # Filter by user if specified in URL parameters
        user_id = self.request.GET.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
            
        # Filter by activity type if specified
        activity_type = self.request.GET.get('type')
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)
            
        # Ensure IP address is captured for viewing activities
        ip_address = get_client_ip(self.request)
        log_activity(
            request=self.request,
            activity_type='view_activity_log',
            description='Viewed activity log',
            record=None
        )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Activity Log'
        context['activity_types'] = dict(UserActivity.ACTIVITY_TYPES)
        context['selected_user'] = self.request.GET.get('user')
        context['selected_type'] = self.request.GET.get('type')
        return context

@login_required
def record_payback(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    record_id = request.POST.get('record_id')
    amount = Decimal(request.POST.get('amount', 0))
    payment_date = request.POST.get('payment_date')
    payment_method = request.POST.get('payment_method')
    notes = request.POST.get('notes', '')
    
    try:
        record = Record.objects.get(id=record_id, transaction_type='advance')
    except Record.DoesNotExist:
        return JsonResponse({'error': 'Record not found'}, status=404)
    
    # Calculate remaining amount
    total_paid = AdvancePayback.objects.filter(advance=record).aggregate(
        Sum('amount'))['amount__sum'] or 0
    remaining = record.amount - total_paid
    
    # Validate payment amount
    if amount <= 0 or amount > remaining:
        return JsonResponse({'error': 'Invalid payment amount'}, status=400)
    
    # Create payback record
    payback = AdvancePayback.objects.create(
        advance=record,
        amount=amount,
        payment_date=payment_date,
        payment_method=payment_method,
        notes=notes,
        created_by=request.user
    )
    
    # Check if advance is fully paid
    new_remaining = remaining - amount
    if new_remaining == 0:
        payback.is_fully_paid = True
        payback.save()
    
    messages.success(request, f'Payment of {amount} AFN recorded successfully')
    return redirect('website:home')

@login_required
def record_installments(request, record_id):
    try:
        record = Record.objects.get(id=record_id, transaction_type='advance')
    except Record.DoesNotExist:
        return JsonResponse({'error': 'Record not found'}, status=404)
    
    installments = AdvancePayback.objects.filter(advance=record).order_by('payment_date')
    
    data = {
        'installments': [
            {
                'date': payment.payment_date.strftime('%Y-%m-%d'),
                'amount': float(payment.amount),
                'method': payment.get_payment_method_display(),
                'notes': payment.notes
            }
            for payment in installments
        ]
    }
    
    return JsonResponse(data)

@login_required
def advance_repayment(request, pk):
    """Handle advance repayment"""
    advance = get_object_or_404(Record, pk=pk, transaction_type='advance')
    
    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount', 0))
        payment_method = request.POST.get('payment_method')
        notes = request.POST.get('notes', '')
        
        # Calculate total paid so far
        total_paid = AdvancePayback.objects.filter(advance=advance).aggregate(Sum('amount'))['amount__sum'] or 0
        remaining_amount = advance.amount - total_paid
        
        # Validate payment amount
        if amount <= 0:
            messages.error(request, 'Payment amount must be greater than zero.')
            return redirect('website:record_detail', pk=pk)
        
        if amount > remaining_amount:
            messages.error(request, f'Payment amount cannot exceed remaining amount ({remaining_amount}).')
            return redirect('website:record_detail', pk=pk)
        
        # Create payback record
        payback = AdvancePayback.objects.create(
            advance=advance,
            amount=amount,
            payment_date=timezone.now().date(),
            payment_method=payment_method,
            notes=notes,
            created_by=request.user,
            is_fully_paid=(amount >= remaining_amount)
        )
        
        # Create activity log
        UserActivity.objects.create(
            user=request.user,
            activity_type='advance_repayment',
            description=f'Repaid {amount} for advance {advance.reference_number}',
            record=advance
        )
        
        messages.success(request, f'Payment of {amount} recorded successfully.')
        return redirect('website:record_detail', pk=pk)
    
    # Get remaining amount
    total_paid = AdvancePayback.objects.filter(advance=advance).aggregate(Sum('amount'))['amount__sum'] or 0
    remaining_amount = advance.amount - total_paid
    
    context = {
        'advance': advance,
        'remaining_amount': remaining_amount,
        'payment_methods': AdvancePayback.PAYMENT_METHODS,
    }
    
    return render(request, 'website/advance_repayment.html', context)

@login_required
def payable_repayment(request, pk):
    """Handle payable record repayment."""
    record = get_object_or_404(Record, pk=pk, transaction_type='payable')
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method')
        payment_date = request.POST.get('payment_date')
        notes = request.POST.get('notes', '')
        
        if not all([amount, payment_method, payment_date]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('website:record_detail', pk=pk)
        
        try:
            amount = Decimal(amount)
            if amount <= 0:
                messages.error(request, 'Amount must be greater than zero.')
                return redirect('website:record_detail', pk=pk)
            
            if amount > record.amount:
                messages.error(request, 'Payment amount cannot exceed the payable amount.')
                return redirect('website:record_detail', pk=pk)
            
            # Update payable record
            if amount >= record.amount:
                record.is_paid = True
                record.save()
            
            # Create user activity
            UserActivity.objects.create(
                user=request.user,
                activity_type='record_update',
                description=f'Recorded payment of {amount} AFN for payable {record.reference_number}',
                record=record
            )
            
            # Create notification for record creator
            Notification.objects.create(
                user=record.created_by,
                title='Payable Payment Recorded',
                message=f'A payment of {amount} AFN has been recorded for your payable record {record.reference_number}.',
                record=record
            )
            
            messages.success(request, f'Payment of {amount} AFN has been recorded successfully.')
            
        except (ValueError, decimal.InvalidOperation) as e:
            messages.error(request, f'Invalid amount format: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error processing payment: {str(e)}')
            
    return redirect('website:record_detail', pk=pk)

# Add to existing views
class PayableRecordListView(RecordListView):
    def get_queryset(self):
        return super().get_queryset().filter(transaction_type='payable')

@login_required
def delete_all_records(request):
    """Delete all records and reset the database sequence. Only accessible by admin users."""
    if not request.user.is_superuser:
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('website:home')
    
    if request.method == 'POST':
        try:
            # Delete all records
            Record.objects.all().delete()
            
            # Reset the sequence for the Record model
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM sqlite_sequence WHERE name='website_record'")
            
            # Create activity log
            UserActivity.objects.create(
                user=request.user,
                activity_type='record_delete',
                description='Deleted all records and reset database sequence'
            )
            
            messages.success(request, "All records have been deleted and the database sequence has been reset.")
        except Exception as e:
            messages.error(request, f"Error deleting records: {str(e)}")
    
    return redirect('website:home')

@login_required
def profile_view(request):
    context = {
        'total_transactions': Transaction.objects.filter(user=request.user).count(),
        'pending_transactions': Transaction.objects.filter(user=request.user, status='pending').count(),
        'completed_transactions': Transaction.objects.filter(user=request.user, status='completed').count(),
    }
    return render(request, 'accounts/profile.html', context)
