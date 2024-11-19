from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import transaction
from decimal import Decimal
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User  # Import the default User model

class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=5)
    exchange_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=4,
        validators=[MinValueValidator(0)]
    )
    is_default = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Currencies"

    def __str__(self):
        return f"{self.code} - {self.name}"

class Transaction(models.Model):
    INCOME = 'income'
    EXPENSE = 'expense'
    ADVANCE = 'advance'
    
    TRANSACTION_TYPE_CHOICES = [
        (INCOME, 'Income'),
        (EXPENSE, 'Expense'),
        (ADVANCE, 'Advance'),
    ]

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('first_approval', 'First Approval'),
        ('second_approval', 'Second Approval'),
        ('final_approval', 'Final Approval'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    )

    CASHIER_STATUS_CHOICES = (
        ('PAID', 'Paid'),
        ('UNPAID', 'Unpaid'),
        ('PENDING', 'Pending'),
    )

    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPE_CHOICES,
        default=EXPENSE
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_transactions')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    cashier_status = models.CharField(max_length=20, choices=CASHIER_STATUS_CHOICES, default='PENDING')
    current_approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='pending_approvals')
    currency = models.ForeignKey('Currency', on_delete=models.PROTECT, related_name='transactions', null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='requested_transactions',
        default=1
    )
    version = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.pk:  # New instance
            self.version = 1
        else:
            self.version += 1
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['status', 'cashier_status']),
            models.Index(fields=['created_at']),
        ]

class Budget(models.Model):
    PERIOD_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]

    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField()
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)

    def get_spent_amount(self):
        return self.category.transactions.filter(
            date__range=[self.start_date, self.end_date]
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or 0

    def get_remaining_amount(self):
        return self.amount - self.get_spent_amount()

class RecurringTransaction(models.Model):
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    next_due_date = models.DateField()
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def generate_transaction(self):
        from datetime import timedelta
        
        if not self.is_active or (self.end_date and self.next_due_date > self.end_date):
            return None

        transaction = Transaction.objects.create(
            amount=self.amount,
            description=self.description,
            currency=self.currency,
            category=self.category,
            created_by=self.created_by,
            date=self.next_due_date
        )

        # Update next due date
        if self.frequency == 'daily':
            self.next_due_date += timedelta(days=1)
        elif self.frequency == 'weekly':
            self.next_due_date += timedelta(weeks=1)
        elif self.frequency == 'monthly':
            self.next_due_date = self.next_due_date.replace(
                month=self.next_due_date.month % 12 + 1,
                year=self.next_due_date.year + (self.next_due_date.month == 12)
            )
        else:  # yearly
            self.next_due_date = self.next_due_date.replace(year=self.next_due_date.year + 1)

        self.save()
        return transaction

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

# If you're using a custom User model:
class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('superadmin', 'Super Admin'),
        ('data_entry', 'Data Entry'),
        ('deputy_director', 'Deputy Director'),
        ('executive_director', 'Executive Director'),
        ('chief_executive', 'Chief Executive'),
        ('regular_user', 'Regular User'),
    ]
    
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='regular_user'
    )

    # Add these related_name attributes to avoid the clash
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='accounts_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='accounts_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def ensure_profile_exists(self):
        """Ensure that a UserProfile exists for this user."""
        UserProfile.objects.get_or_create(user=self)

class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    user_type = models.CharField(
        max_length=20,
        choices=[
            ('superadmin', 'Super Admin'),
            ('data_entry', 'Data Entry'),
            ('cashier', 'Cashier'),
        ]
    )

    def __str__(self):
        return f"{self.user.username}'s profile"