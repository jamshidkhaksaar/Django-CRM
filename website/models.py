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
    TRANSACTION_TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('advance', 'Advance'),
    ]

    ITEM_TYPE_CHOICES = [
        ('it_equipment', 'IT Equipment'),
        ('furniture', 'Furniture'),
        ('vehicle', 'Vehicle'),
        ('stationary', 'Stationary'),
        ('appliances', 'Appliances'),
        ('electronics', 'Electronics'),
        ('consumables', 'Consumables'),
        ('office_decor', 'Office Décor'),
        ('cleaning_supplies', 'Cleaning Supplies'),
        ('safety_equipment', 'Safety Equipment'),
        ('documents_files', 'Documents and Files'),
        ('tools', 'Tools'),
    ]

    PROJECT_CHOICES = [
        ('drc', 'DRC'),
        ('nca', 'NCA'),
        ('giz', 'GIZ'),
        ('mc', 'MC'),
        ('aware', 'AWARE'),
    ]

    LOCATION_CHOICES = [
        ('badakhshan', 'Badakhshan'),
        ('badghis', 'Badghis'),
        ('baghlan', 'Baghlan'),
        ('balkh', 'Balkh'),
        ('bamyan', 'Bamyan'),
        ('daykundi', 'Daykundi'),
        ('farah', 'Farah'),
        ('faryab', 'Faryab'),
        ('ghazni', 'Ghazni'),
        ('ghor', 'Ghor'),
        ('helmand', 'Helmand'),
        ('herat', 'Herat'),
        ('jawzjan', 'Jawzjan'),
        ('kabul', 'Kabul'),
        ('kandahar', 'Kandahar'),
        ('kapisa', 'Kapisa'),
        ('khost', 'Khost'),
        ('kunar', 'Kunar'),
        ('kunduz', 'Kunduz'),
        ('laghman', 'Laghman'),
        ('logar', 'Logar'),
        ('nangarhar', 'Nangarhar'),
        ('nimroz', 'Nimroz'),
        ('nuristan', 'Nuristan'),
        ('paktia', 'Paktia'),
        ('paktika', 'Paktika'),
        ('panjshir', 'Panjshir'),
        ('parwan', 'Parwan'),
        ('samangan', 'Samangan'),
        ('sar_e_pul', 'Sar-e-Pul'),
        ('takhar', 'Takhar'),
        ('urozgan', 'Urozgan'),
        ('wardak', 'Wardak (Maidan Wardak)'),
        ('zabul', 'Zabul'),
    ]

    UNIT_MEASURE_CHOICES = [
        ('pc', 'PC'),
        ('box', 'BOX'),
        ('pk', 'PK'),
        ('kg', 'KG'),
        ('lb', 'LB'),
        ('l', 'L'),
        ('ml', 'ML'),
        ('m', 'M'),
        ('cm', 'CM'),
        ('in', 'IN'),
        ('ft', 'FT'),
        ('dozen', 'DOZEN'),
        ('set', 'SET'),
        ('pair', 'PAIR'),
        ('roll', 'ROLL'),
        ('bundle', 'BUNDLE'),
        ('carton', 'CARTON'),
        ('case', 'CASE'),
        ('gb', 'GB'),
        ('tb', 'TB'),
        ('ea', 'EA'),
        ('sheet', 'SHEET'),
        ('bag', 'BAG'),
        ('tube', 'TUBE'),
        ('can', 'CAN'),
        ('drum', 'DRUM'),
        ('pallet', 'PALLET'),
        ('unit', 'UNIT'),
        ('lot', 'LOT'),
    ]

    REVIEWER_CHOICES = [
        ('committee', 'Committee'),
        ('deputy_director', 'Deputy Director'),
        ('executive_director', 'Executive Director'),
        ('chief_executive_director', 'Chief Executive Director'),
    ]

    APPROVAL_CHOICES = [
        ('approved', 'Approved'),
        ('declined', 'Declined'),
        ('pending', 'Pending'),
        ('postponed', 'Postponed'),
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    item_name = models.CharField(max_length=100)
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES)
    description = models.TextField()
    project = models.CharField(max_length=20, choices=PROJECT_CHOICES)
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES)
    requester = models.CharField(max_length=100)
    unit_measure = models.CharField(max_length=20, choices=UNIT_MEASURE_CHOICES)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_value = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    date = models.DateField(default=timezone.now)
    reviewer = models.CharField(max_length=50, choices=REVIEWER_CHOICES)
    reviewer_result = models.CharField(max_length=100)
    approval = models.CharField(max_length=20, choices=APPROVAL_CHOICES)
    cashier_status = models.CharField(max_length=100)
    comments = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        # Calculate total value
        self.total_value = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item_name} - {self.transaction_type}"