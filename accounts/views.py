from django.shortcuts import render
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from .models import Transaction

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
