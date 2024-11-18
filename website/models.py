from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
from django.urls import reverse

class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Adds additional fields for user type, department, and phone.
    """
    USER_TYPE_CHOICES = (
        ('superadmin', 'Super Admin'),
        ('data_entry', 'Data Entry User'),
        ('cashier', 'Cashier'),
        ('deputy_director', 'Deputy Director'),
        ('executive_director', 'Executive Director'),
        ('chief_executive', 'Chief Executive Director'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    department = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return f"{self.username} - {self.get_user_type_display()}"

class Record(models.Model):
    """
    Model representing a transaction record.
    Contains various fields to capture transaction details.
    """
    TRANSACTION_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('advance', 'Advance'),
    ]
    
    REVIEWER_RESULT_CHOICES = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('pending', 'Pending'),
    ]
    
    APPROVAL_CHOICES = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('pending', 'Pending'),
    ]
    
    CASHIER_STATUS_CHOICES = [
        ('PAID', 'Paid'),
        ('UNPAID', 'Unpaid'),
        ('PENDING', 'Pending'),
    ]

    transaction_type = models.CharField(max_length=30, choices=TRANSACTION_CHOICES)
    item_name = models.CharField(max_length=100)
    item_type = models.CharField(max_length=100)
    description = models.TextField()
    project = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    unit_measure = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_value = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    reviewer = models.ForeignKey(
        'CustomUser',  # Reference to the CustomUser model
        on_delete=models.CASCADE,  # Choose appropriate behavior on delete
        related_name='records',  # Optional: allows reverse access from CustomUser
        null=True,  # Allow null if a reviewer is not always required
        blank=True,  # Allow blank in forms
    )
    reviewer_result = models.CharField(max_length=50, choices=REVIEWER_RESULT_CHOICES)
    approval = models.CharField(max_length=50, choices=APPROVAL_CHOICES)
    cashier_status = models.CharField(max_length=50, choices=CASHIER_STATUS_CHOICES)
    version = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        # Use a transaction to ensure atomicity
        with transaction.atomic():
            # Calculate total value using Decimal
            self.total_value = Decimal(self.quantity) * Decimal(self.unit_price)
            # Round total_value to 2 decimal places
            self.total_value = self.total_value.quantize(Decimal('0.01'))  # Rounding to 2 decimal places
            
            # Increment the version number on save
            self.version += 1
            
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_type} - {self.item_name}"

    def get_absolute_url(self):
        return reverse('edit_record', args=[str(self.id)])

class DefaultChoices(models.Model):
    item_types = models.JSONField(default=list)
    projects = models.JSONField(default=list)
    locations = models.JSONField(default=list)
    unit_measures = models.JSONField(default=list)
    reviewers = models.JSONField(default=list)

    def __str__(self):
        return "Default Choices"