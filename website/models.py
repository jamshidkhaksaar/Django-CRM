from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Adds additional fields for user type, department, and phone.
    """
    USER_TYPE_CHOICES = (
        ('superadmin', 'Super Admin'),
        ('data_entry', 'Data Entry User'),
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

    transaction_type = models.CharField(max_length=100, choices=TRANSACTION_CHOICES)
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
    reviewer = models.CharField(max_length=100)
    reviewer_result = models.CharField(max_length=50, choices=REVIEWER_RESULT_CHOICES)
    approval = models.CharField(max_length=50, choices=APPROVAL_CHOICES)
    cashier_status = models.CharField(max_length=50, choices=CASHIER_STATUS_CHOICES)

    def save(self, *args, **kwargs):
        # Calculate total value
        self.total_value = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_type} - {self.item_name}"