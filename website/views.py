from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import logout, authenticate, login
from django.shortcuts import redirect
from django.http import HttpResponse
from .forms import AddRecordForm
from .models import Record
from django.db.models import Sum, Case, When, DecimalField
from django.db.models.functions import TruncMonth
from decimal import Decimal
from django.db.models import Q
from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .decorators import user_type_required
from .models import Notification
from accounts.models import UserProfile
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.functions import TruncMonth
import json

@login_required
def pending_records(request):
    user = request.user
    
    # Define status mapping for different user types
    status_mapping = {
        'deputy_director': 'pending_deputy',
        'executive_director': 'pending_executive',
        'chief_executive': 'pending_chief'
    }
    
    if user.user_type == 'superadmin':
        records = Record.objects.exclude(approval_status='approved')
    elif user.user_type in status_mapping:
        records = Record.objects.filter(approval_status=status_mapping[user.user_type])
    else:
        records = Record.objects.filter(
            Q(requester=user) & ~Q(approval_status='approved')
        )
    
    records = records.order_by('-date')
    
    context = {
        'records': records,
        'user_type': user.user_type,
        'can_approve': user.can_approve_records(),
        'status_to_approve': status_mapping.get(user.user_type),
        'total_records': records.count(),
        'total_pending': records.filter(approval_status__startswith='pending').count(),
        'total_rejected': records.filter(approval_status='rejected').count()
    }
    return render(request, 'pending_records.html', context)

@login_required
def approved_records(request):
    # Get or create user profile from accounts app
    userprofile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'user_type': 'data_entry'}  # Set default user type
    )
    
    user_type = userprofile.user_type
    records = Record.objects.filter(approval_status='approved')
    can_edit = user_type in ['superadmin', 'data_entry']
    
    context = {
        'records': records,
        'can_edit': can_edit,
        'user_type': user_type,
    }
    
    return render(request, 'approved_records.html', context)

@login_required
def rejected_records(request):
    user = request.user
    records = Record.objects.filter(approval_status='rejected').order_by('-date')
    
    # Get user type safely
    try:
        user_type = request.user.userprofile.user_type
    except UserProfile.DoesNotExist:
        user_type = None  # or set a default value
    
    # Calculate totals for rejected records
    try:
        can_edit = user_type in ['superadmin', 'data_entry']
    except UserProfile.DoesNotExist:
        can_edit = False  # or handle this case as needed
    
    context = {
        'records': records,
        'total_records': records.count(),
        'total_income': records.filter(transaction_type='income').aggregate(
            Sum('total_value'))['total_value__sum'] or Decimal('0.00'),
        'total_expense': records.filter(transaction_type='expense').aggregate(
            Sum('total_value'))['total_value__sum'] or Decimal('0.00'),
        'total_advance': records.filter(transaction_type='advance').aggregate(
            Sum('total_value'))['total_value__sum'] or Decimal('0.00'),
        'can_edit': can_edit
    }
    return render(request, 'rejected_records.html', context)

@login_required
def home(request):
    records = Record.objects.only(
        'id',
        'transaction_type',
        'item_name',
        'item_type',
        'description',
        'project',
        'location',
        'requester',
        'unit_measure',
        'quantity',
        'unit_price',
        'total_value',
        'date',
        'reviewer',
        'approval_status',
        'cashier_status',
        'comments',
        'created_at',
        'updated_at',
        'chief_executive_approval',
        'deputy_director_approval',
        'executive_director_approval'
    ).all()
    
    # Calculate totals
    total_income = Record.objects.filter(transaction_type='income').aggregate(Sum('total_value'))['total_value__sum'] or 0
    total_expense = Record.objects.filter(transaction_type='expense').aggregate(Sum('total_value'))['total_value__sum'] or 0
    total_advance = Record.objects.filter(transaction_type='advance').aggregate(Sum('total_value'))['total_value__sum'] or 0
    total_balance = total_income - total_expense - total_advance
    
    # Get notifications
    notifications_queryset = Notification.objects.filter(user=request.user)
    notifications = notifications_queryset.order_by('-created_at')[:5]
    unread_notifications = notifications_queryset.filter(is_read=False).count()
    
    context = {
        'records': records,
        'total_income': total_income,
        'total_expense': total_expense,
        'total_advance': total_advance,
        'total_balance': total_balance,
        'add_record_form': AddRecordForm(),
        'notifications': notifications,
        'unread_notifications': unread_notifications,
    }
    return render(request, 'home.html', context)

def add_record(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 'error',
            'message': 'Please log in to add records'
        }, status=401)

    if request.method == 'POST':
        form = AddRecordForm(request.POST)
        if form.is_valid():
            try:
                record = form.save(commit=False)
                CustomUser = get_user_model()
                current_user = CustomUser.objects.get(id=request.user.id)
                
                record.reviewer = current_user
                record.requester = current_user
                record.reviewer_result = 'pending'
                record.save()
                
                return JsonResponse({'status': 'success'})
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                }, status=400)
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Form validation failed',
                'errors': {field: [str(e) for e in errors] for field, errors in form.errors.items()}
            }, status=400)
    else:
        form = AddRecordForm()
    
    return render(request, 'add_record.html', {'form': form})

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

def logout_user(request):
    logout(request)
    return redirect('home')

def register_user(request):
    return render(request, 'register.html')

@login_required
def my_records(request):
    user = request.user
    records = Record.objects.filter(requester=user).order_by('-date')
    
    context = {
        'records': records,
        'total_records': records.count(),
        'pending_count': records.filter(approval_status__startswith='pending').count(),
        'approved_count': records.filter(approval_status='approved').count(),
        'rejected_count': records.filter(approval_status='rejected').count(),
        'can_edit': user.user_type in ['superadmin', 'data_entry']
    }
    return render(request, 'my_records.html', context)

def dashboard(request):
    # Get total counts
    total_records = Record.objects.count()
    pending_count = Record.objects.filter(reviewer_result='pending').count()
    approved_count = Record.objects.filter(reviewer_result='approved').count()
    rejected_count = Record.objects.filter(reviewer_result='rejected').count()
    
    # Get financial summaries
    total_income = Record.objects.filter(
        transaction_type='income'
    ).aggregate(Sum('total_value'))['total_value__sum'] or Decimal('0.00')
    
    total_expense = Record.objects.filter(
        transaction_type='expense'
    ).aggregate(Sum('total_value'))['total_value__sum'] or Decimal('0.00')
    
    total_advance = Record.objects.filter(
        transaction_type='advance'
    ).aggregate(Sum('total_value'))['total_value__sum'] or Decimal('0.00')
    
    # Calculate total balance
    total_balance = total_income - total_expense - total_advance
    
    # Get recent records with specific fields only
    recent_records = Record.objects.only(
        'date',
        'transaction_type',
        'item_name',
        'total_value',
        'reviewer_result'
    ).order_by('-date')[:5]
    
    # Get monthly data for charts
    monthly_data = Record.objects.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        income=Sum(Case(
            When(transaction_type='income', then='total_value'),
            default=0,
            output_field=DecimalField(),
        )),
        expense=Sum(Case(
            When(transaction_type='expense', then='total_value'),
            default=0,
            output_field=DecimalField(),
        ))
    ).order_by('month')
    
    # Prepare data for charts
    monthly_labels = [d['month'].strftime("%B %Y") for d in monthly_data]
    monthly_income = [float(d['income']) for d in monthly_data]
    monthly_expense = [float(d['expense']) for d in monthly_data]
    
    # Get expense categories data (using item_type instead of category)
    expense_categories_data = Record.objects.filter(
        transaction_type='expense'
    ).values('item_type').annotate(
        total=Sum('total_value')
    ).order_by('-total')[:5]
    
    expense_categories = [d['item_type'] for d in expense_categories_data]
    category_amounts = [float(d['total']) for d in expense_categories_data]
    
    context = {
        'total_records': total_records,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'total_income': total_income,
        'total_expense': total_expense,
        'total_advance': total_advance,
        'total_balance': total_balance,
        'recent_records': recent_records,
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_income': json.dumps(monthly_income),
        'monthly_expense': json.dumps(monthly_expense),
        'expense_categories': json.dumps(expense_categories),
        'category_amounts': json.dumps(category_amounts),
    }
    
    return render(request, 'dashboard.html', context)

def edit_record(request, pk):
    record = get_object_or_404(Record, pk=pk)
    if request.method == 'POST':
        form = AddRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = AddRecordForm(instance=record)
    
    context = {
        'form': form,
        'record': record
    }
    return render(request, 'edit_record.html', context)

def delete_record(request, pk):
    record = get_object_or_404(Record, pk=pk)
    if request.method == 'POST':
        record.delete()
        return redirect('home')
    return render(request, 'delete_record.html', {'record': record})

@login_required
def record_detail(request, pk):
    record = get_object_or_404(Record, pk=pk)
    user = request.user
    
    # Determine if the current user can approve this record
    can_approve = False
    if user.user_type == 'deputy_director' and record.approval_status == 'pending_deputy':
        can_approve = True
    elif user.user_type == 'executive_director' and record.approval_status == 'pending_executive':
        can_approve = True
    elif user.user_type == 'chief_executive' and record.approval_status == 'pending_chief':
        can_approve = True
        
    # Get approval history
    approval_history = []
    if record.deputy_director_approval:
        approval_history.append({
            'approver': user,
            'role': 'Deputy Director',
            'date': timezone.now(),
            'comments': record.deputy_director_comments
        })
    if record.executive_director_approval:
        approval_history.append({
            'approver': user,
            'role': 'Executive Director',
            'date': timezone.now(),
            'comments': record.executive_director_comments
        })
    if record.chief_executive_approval:
        approval_history.append({
            'approver': user,
            'role': 'Chief Executive',
            'date': timezone.now(),
            'comments': record.chief_executive_comments
        })
    
    context = {
        'record': record,
        'can_approve': can_approve,
        'can_edit': user.user_type in ['superadmin', 'data_entry'] or user == record.requester,
        'approval_history': approval_history,
        'notifications': Notification.objects.filter(record=record).order_by('-created_at')[:5]
    }
    return render(request, 'record_detail.html', context)

@login_required
@user_type_required('deputy_director', 'executive_director', 'chief_executive')
def record_approval(request, pk):
    record = get_object_or_404(Record, pk=pk)
    user = request.user
    
    if request.method == 'POST':
        status = request.POST.get('status')
        comments = request.POST.get('comments', '')
        
        try:
            # Use the process_approval method from the Record model
            record.process_approval(user, status, comments)
            
            # Create notification for record owner
            Notification.objects.create(
                user=record.requester,
                record=record,
                message=f'Your record #{record.id} has been {status} by {user.get_full_name()}'
            )
            
            # Create notification for next approver if applicable
            if status == 'approved' and user.user_type != 'chief_executive':
                next_approver_type = {
                    'deputy_director': 'executive_director',
                    'executive_director': 'chief_executive'
                }[user.user_type]
                
                next_approvers = User.objects.filter(user_type=next_approver_type)
                for approver in next_approvers:
                    Notification.objects.create(
                        user=approver,
                        record=record,
                        message=f'New record #{record.id} requires your approval'
                    )
            
            messages.success(request, f"Record has been {status}")
            return redirect('record_detail', pk=pk)
            
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('record_detail', pk=pk)
    
    return render(request, 'approval_form.html', {
        'record': record,
        'can_approve': True,
        'previous_approvals': record.approval_history or []
    })

@login_required
def notifications(request):
    notifications_queryset = Notification.objects.filter(user=request.user)
    context = {
        'notifications': notifications_queryset.order_by('-created_at'),
        'unread_count': notifications_queryset.filter(is_read=False).count()
    }
    return render(request, 'notifications.html', context)

@login_required
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'success'})

@login_required
def mark_all_notifications_read(request):
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=405)

@login_required
@user_type_required('superadmin')
def user_list(request):
    users = get_user_model().objects.all().order_by('-date_joined')
    context = {
        'users': users
    }
    return render(request, 'user_list.html', context)

@login_required
@user_type_required('superadmin')
def create_user(request):
    if request.method == 'POST':
        # Add user creation logic here
        pass
    return render(request, 'create_user.html')