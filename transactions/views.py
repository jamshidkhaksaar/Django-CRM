from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.urls import reverse_lazy
from .models import Transaction, Budget
from .forms import TransactionForm

class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'transactions/list.html'
    context_object_name = 'transactions'
    
    def get_queryset(self):
        if self.request.user.user_type == 'admin':
            return Transaction.objects.all()
        return Transaction.objects.filter(created_by=self.request.user)

class TransactionDetailView(LoginRequiredMixin, DetailView):
    model = Transaction
    template_name = 'transactions/detail.html'
    context_object_name = 'transaction'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_approve'] = (
            self.request.user.user_type in ['admin', 'staff'] and 
            self.object.status == 'pending'
        )
        return context

class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'transactions/form.html'
    success_url = reverse_lazy('transactions:list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class TransactionApproveView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Transaction
    fields = []
    success_url = reverse_lazy('transactions:list')
    
    def test_func(self):
        return self.request.user.user_type in ['admin', 'staff']
    
    def form_valid(self, form):
        form.instance.status = 'approved'
        return super().form_valid(form)

class TransactionRejectView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Transaction
    fields = []
    success_url = reverse_lazy('transactions:list')
    
    def test_func(self):
        return self.request.user.user_type in ['admin', 'staff']
    
    def form_valid(self, form):
        form.instance.status = 'rejected'
        return super().form_valid(form) 