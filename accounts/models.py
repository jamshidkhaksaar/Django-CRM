from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPES = (
        ('cashier', 'Cashier'),
        ('deputy_director', 'Deputy Executive Director'),
        ('executive_director', 'Executive Director'),
        ('chief_executive', 'Chief Executive Director'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPES, null=True, blank=True)

class Transaction(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('first_approval', 'First Approval'),
        ('second_approval', 'Second Approval'),
        ('final_approval', 'Final Approval'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_transactions')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    current_approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='pending_approvals')