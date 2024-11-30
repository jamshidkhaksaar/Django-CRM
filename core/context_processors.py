from transactions.models import Transaction

def common_context(request):
    context = {}
    if request.user.is_authenticated:
        context['pending_approvals'] = (
            Transaction.objects.filter(status='pending').count()
            if request.user.user_type == 'admin'
            else 0
        )
    return context 