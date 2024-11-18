from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm, AddRecordForm
from .models import Record, DefaultChoices, CustomUser
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncMonth
import json
from datetime import datetime, timedelta
import logging
from django.contrib.auth.decorators import login_required
from .decorators import user_type_required
from django.http import HttpResponseForbidden

logger = logging.getLogger(__name__)

def get_filter_choices(records):
    """Helper function to get unique values for filter dropdowns"""
    return {
        'transaction_types': records.values_list('transaction_type', flat=True).distinct().order_by('transaction_type'),
        'item_names': records.values_list('item_name', flat=True).distinct().order_by('item_name'),
        'item_types': records.values_list('item_type', flat=True).distinct().order_by('item_type'),
        'descriptions': records.values_list('description', flat=True).distinct().order_by('description'),
        'projects': records.values_list('project', flat=True).distinct().order_by('project'),
        'locations': records.values_list('location', flat=True).distinct().order_by('location'),
        'requesters': records.values_list('requester', flat=True).distinct().order_by('requester'),
        'unit_measures': records.values_list('unit_measure', flat=True).distinct().order_by('unit_measure'),
        'quantities': records.values_list('quantity', flat=True).distinct().order_by('quantity'),
        'unit_prices': records.values_list('unit_price', flat=True).distinct().order_by('unit_price'),
        'total_values': records.values_list('total_value', flat=True).distinct().order_by('total_value'),
        'dates': records.values_list('date', flat=True).distinct().order_by('-date'),
        'reviewers': records.values_list('reviewer', flat=True).distinct().order_by('reviewer'),
        'reviewer_results': records.values_list('reviewer_result', flat=True).distinct().order_by('reviewer_result'),
        'approvals': records.values_list('approval', flat=True).distinct().order_by('approval'),
        'statuses': records.values_list('cashier_status', flat=True).distinct().order_by('cashier_status'),
        'comments': records.values_list('comments', flat=True).distinct().order_by('comments'),
    }

def home(request):
    if request.user.is_authenticated:
        # Get your records
        records = Record.objects.all()
        form = AddRecordForm()
        
        # Fetch default choices from the database
        default_choices = DefaultChoices.objects.first()  # Assuming only one entry exists

        # Initialize default values
        item_types = []
        projects = []
        locations = []
        unit_measures = []
        reviewers = []

        # Get unique values from existing records for choices
        if default_choices is not None:
            item_types = Record.objects.values_list('item_type', flat=True).distinct() or default_choices.item_types
            projects = Record.objects.values_list('project', flat=True).distinct() or default_choices.projects
            locations = Record.objects.values_list('location', flat=True).distinct() or default_choices.locations
            unit_measures = Record.objects.values_list('unit_measure', flat=True).distinct() or default_choices.unit_measures
            reviewers = Record.objects.values_list('reviewer', flat=True).distinct() or default_choices.reviewers
        else:
            # If no default choices exist, get unique values from records
            item_types = Record.objects.values_list('item_type', flat=True).distinct()
            projects = Record.objects.values_list('project', flat=True).distinct()
            locations = Record.objects.values_list('location', flat=True).distinct()
            unit_measures = Record.objects.values_list('unit_measure', flat=True).distinct()
            reviewers = Record.objects.values_list('reviewer', flat=True).distinct()

        # Calculate totals
        total_income = records.filter(transaction_type='income').aggregate(Sum('total_value'))['total_value__sum'] or 0
        total_expense = records.filter(transaction_type='expense').aggregate(Sum('total_value'))['total_value__sum'] or 0
        total_advance = records.filter(transaction_type='advance').aggregate(Sum('total_value'))['total_value__sum'] or 0

        context = {
            'records': records,
            'form': form,
            'item_types': item_types,
            'projects': projects,
            'locations': locations,
            'unit_measures': unit_measures,
            'reviewers': reviewers,
            'total_income': total_income,
            'total_expense': total_expense,
            'total_advance': total_advance,
        }
        return render(request, 'home.html', context)
    
    return render(request, 'home.html', {})

def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'register.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        logger.info("="*50)
        logger.info(f"Login attempt for: {username}")
        
        try:
            # First check if user exists
            user = CustomUser.objects.get(username=username)
            logger.info(f"Found user: {username}")
            logger.info(f"Is active: {user.is_active}")
            
            # Attempt authentication
            auth_user = authenticate(request, username=username, password=password)
            
            if auth_user is not None:
                login(request, auth_user)
                logger.info(f"Login successful for: {username}")
                messages.success(request, "You have been logged in.")
                return redirect('home')
            else:
                logger.warning(f"Invalid password for: {username}")
                messages.error(request, "Invalid password.")
            
        except CustomUser.DoesNotExist:
            logger.warning(f"User not found: {username}")
            messages.error(request, "Invalid username.")
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            messages.error(request, "An error occurred during login.")
        
        logger.info("="*50)
        return redirect('home')
    
    return redirect('home')

def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')

def customer_record(request, pk):
    if request.user.is_authenticated:
        customer_record = get_object_or_404(Record, id=pk, requester=request.user)  # Check ownership
        return render(request, 'record.html', {'customer_record': customer_record})
    else: 
        messages.error(request, "You must be logged in to view this page.")
        return redirect('home')

def delete_record(request, pk):
    if request.user.is_authenticated:
        record_to_delete = get_object_or_404(Record, id=pk, requester=request.user)  # Check ownership
        record_to_delete.delete()
        messages.success(request, "Record deleted successfully.")
        return redirect('home')
    else:
        messages.error(request, "You must be logged in to do that.")
        return redirect('home')

@login_required
def add_record(request):
    if request.method == 'POST':
        form = AddRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.requester = request.user
            record.save()
            messages.success(request, "Record Added Successfully!")
            return redirect('home')
    else:
        form = AddRecordForm()
    
    # Return JSON or a partial template instead of full navbar
    return render(request, 'add_record.html', {'form': form})

@login_required
def update_record(request, pk):
    if request.user.is_authenticated:
        current_record = get_object_or_404(Record, id=pk, requester=request.user)  # Check ownership
        form = AddRecordForm(request.POST or None, instance=current_record)
        if request.method == "POST":
            if form.is_valid():
                # Check if the version matches
                if form.instance.version == current_record.version:
                    form.save()
                    messages.success(request, "Record has been updated!")
                    return redirect('home')
                else:
                    messages.error(request, "This record has been modified by another user. Please refresh and try again.")
            else:
                messages.error(request, "There was an error with your form submission. Please correct the errors below.")
        return render(request, 'update_record.html', {'form': form})
    else:
        messages.error(request, "You must be logged in to update a record.")
        return redirect('home')

def filter_records(records, search_query, search_filter):
    """Helper function to filter records based on search query and filter type."""
    if search_query:
        if search_filter == 'all':
            records = records.filter(
                Q(transaction_type__icontains=search_query) |
                Q(item_name__icontains=search_query) |
                Q(project__icontains=search_query) |
                Q(location__icontains=search_query) |
                Q(requester__username__icontains=search_query)
            )
        else:
            if search_filter == 'requester':
                records = records.filter(requester__username__icontains=search_query)
            else:
                filter_kwargs = {f"{search_filter}__icontains": search_query}
                records = records.filter(**filter_kwargs)
    return records

@login_required
def pending_records(request):
    if request.user.is_authenticated:
        records = Record.objects.filter(cashier_status='Pending')
        form = AddRecordForm()
        
        # Add search functionality
        search_query = request.GET.get('search', '')
        search_filter = request.GET.get('filter', 'all')

        records = filter_records(records, search_query, search_filter)

        return render(request, 'home.html', {
            'records': records,
            'form': form,
            'search_query': search_query,
            'search_filter': search_filter
        })
    return redirect('home')

@login_required
def approved_records(request):
    records = Record.objects.filter(cashier_status='Approved')
    form = AddRecordForm()
    
    # Add search functionality
    search_query = request.GET.get('search', '')
    search_filter = request.GET.get('filter', 'all')

    records = filter_records(records, search_query, search_filter)

    return render(request, 'home.html', {
        'records': records,
        'form': form,
        'search_query': search_query,
        'search_filter': search_filter
    })

@login_required
def rejected_records(request):
    if request.user.is_authenticated:
        records = Record.objects.filter(cashier_status='Rejected')
        form = AddRecordForm()
        
        # Add search functionality
        search_query = request.GET.get('search', '')
        search_filter = request.GET.get('filter', 'all')

        records = filter_records(records, search_query, search_filter)

        return render(request, 'home.html', {
            'records': records,
            'form': form,
            'search_query': search_query,
            'search_filter': search_filter
        })
    return redirect('home')

@login_required
def my_records(request):
    if request.user.is_authenticated:
        records = Record.objects.filter(requester=request.user)
        form = AddRecordForm()
        
        # Add search functionality
        search_query = request.GET.get('search', '')
        search_filter = request.GET.get('filter', 'all')

        records = filter_records(records, search_query, search_filter)

        return render(request, 'home.html', {
            'records': records,
            'form': form,
            'search_query': search_query,
            'search_filter': search_filter
        })
    return redirect('home')

@user_type_required('superadmin')
def dashboard(request):
    if request.user.is_authenticated:
        # Get counts for statistics cards
        total_records = Record.objects.count()
        approved_count = Record.objects.filter(cashier_status='Approved').count()
        pending_count = Record.objects.filter(cashier_status='Pending').count()
        rejected_count = Record.objects.filter(cashier_status='Rejected').count()

        # Monthly transactions data (last 6 months)
        six_months_ago = datetime.now() - timedelta(days=180)
        monthly_data = Record.objects.filter(
            date__gte=six_months_ago
        ).annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')

        monthly_labels = [item['month'].strftime("%B %Y") for item in monthly_data]
        monthly_counts = [item['count'] for item in monthly_data]

        # Transaction types data
        transaction_types = Record.objects.values('transaction_type').annotate(
            count=Count('id')
        ).order_by('-count')

        transaction_types_labels = [item['transaction_type'] for item in transaction_types]
        transaction_types_counts = [item['count'] for item in transaction_types]

        # Project value data
        project_data = Record.objects.values('project').annotate(
            total_value=Sum('total_value')
        ).order_by('-total_value')[:5]  # Top 5 projects

        project_labels = [item['project'] for item in project_data]
        project_values = [float(item['total_value']) if item['total_value'] is not None else 0 for item in project_data]

        context = {
            'total_records': total_records,
            'approved_count': approved_count,
            'pending_count': pending_count,
            'rejected_count': rejected_count,
            'monthly_labels': json.dumps(monthly_labels),
            'monthly_data': monthly_counts,
            'transaction_types_labels': json.dumps(transaction_types_labels),
            'transaction_types_data': transaction_types_counts,
            'project_labels': json.dumps(project_labels),
            'project_values': project_values,
        }

        return render(request, 'dashboard.html', context)
    return redirect('home')

def some_view(request):
    if request.user.is_authenticated:
        if request.user.user_type != 'data_entry':
            return HttpResponseForbidden("You do not have permission to access this page.")

        # Proceed with the view logic
    return redirect('login')

@login_required
def edit_record(request, pk):
    record = get_object_or_404(Record, pk=pk)
    
    if request.method == 'POST':
        form = AddRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, "Record Updated Successfully!")
            return redirect('home')
    else:
        form = AddRecordForm(instance=record)
    
    return render(request, 'edit_record.html', {
        'form': form,
        'record': record
    })

@login_required
def delete_record(request, pk):
    record = get_object_or_404(Record, pk=pk)
    if request.method == 'POST':
        record.delete()
        messages.success(request, "Record Deleted Successfully!")
        return redirect('home')
    return redirect('edit_record', pk=pk)