from django.db import models
from django.conf import settings
from django.db.models import Sum
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)

    class Meta:
        app_label = 'website'

    def __str__(self):
        return f"{self.user.username}'s profile"

    @property
    def user_type_display(self):
        return dict(self.user.USER_TYPE_CHOICES).get(self.user.user_type, '')


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    record = models.ForeignKey('Record', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    notification_type = models.CharField(max_length=50, choices=[
        ('record_approval', 'Record Approval'),
        ('record_status', 'Record Status Change'),
        ('record_comment', 'Record Comment'),
        ('system', 'System Notification')
    ], default='system')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])
    
    @property
    def short_message(self):
        """Return truncated message for preview"""
        return self.message[:100] + '...' if len(self.message) > 100 else self.message


class ReferenceNumber(models.Model):
    """Model to track and generate reference numbers"""
    prefix = models.CharField(max_length=10)
    year = models.CharField(max_length=4)
    month = models.CharField(max_length=2)
    sequence = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('prefix', 'year', 'month', 'sequence')

    @classmethod
    def generate_reference_number(cls, transaction_type):
        # Get the prefix based on transaction type
        prefix_map = {
            'income': 'INC',
            'expense': 'EXP',
            'advance': 'ADV',
            'balance': 'BAL'
        }
        prefix = prefix_map.get(transaction_type, 'REC')
        
        # Get current year and month
        current_date = timezone.now()
        year = current_date.strftime('%Y')
        month = current_date.strftime('%m')
        
        # Get or create the next sequence number
        ref_number, created = cls.objects.get_or_create(
            prefix=prefix,
            year=year,
            month=month,
            defaults={'sequence': 1}
        )
        
        if not created:
            ref_number.sequence += 1
            ref_number.save()
        
        # Generate the reference number string
        reference_number = f"{prefix}-{year}{month}-{str(ref_number.sequence).zfill(4)}"
        
        return reference_number


class Record(models.Model):
    TRANSACTION_TYPES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('advance', 'Advance'),
        ('balance', 'Balance'),
        ('payable', 'Payable'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('pending_deputy', 'Pending Deputy Director Approval'),
        ('rejected_deputy', 'Rejected by Deputy Director'),
        ('pending_executive', 'Pending Executive Director Approval'),
        ('rejected_executive', 'Rejected by Executive Director'),
        ('pending_ceo', 'Pending CEO Approval'),
        ('rejected_ceo', 'Rejected by CEO'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    INCOME_SOURCES = (
        ('salary', 'Salary'),
        ('investment', 'Investment'),
        ('donation', 'Donation'),
        ('grant', 'Grant'),
        ('sales', 'Sales'),
        ('service', 'Service Fee'),
        ('other', 'Other'),
    )

    INCOME_CATEGORIES = (
        ('regular', 'Regular Income'),
        ('one-time', 'One-time Income'),
        ('recurring', 'Recurring Income'),
    )

    EXPENSE_CATEGORIES = (
        ('utilities', 'Utilities'),
        ('supplies', 'Office Supplies'),
        ('maintenance', 'Maintenance'),
        ('salary', 'Salary Payments'),
        ('rent', 'Rent'),
        ('equipment', 'Equipment'),
        ('transportation', 'Transportation'),
        ('other', 'Other'),
    )

    EXPENSE_TYPES = (
        ('operational', 'Operational'),
        ('administrative', 'Administrative'),
        ('project', 'Project-based'),
        ('emergency', 'Emergency'),
    )

    BALANCE_TYPES = (
        ('opening', 'Opening Balance'),
        ('closing', 'Closing Balance'),
        ('adjustment', 'Balance Adjustment'),
        ('reconciliation', 'Bank Reconciliation'),
    )

    PAYMENT_METHODS = (
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('check', 'Check'),
        ('online', 'Online Payment'),
    )

    # Common fields
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField()
    reference_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Income fields
    income_source = models.CharField(max_length=50, choices=INCOME_SOURCES, null=True, blank=True)
    income_category = models.CharField(max_length=50, choices=INCOME_CATEGORIES, null=True, blank=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS, null=True, blank=True)

    # Expense fields
    expense_category = models.CharField(max_length=50, choices=EXPENSE_CATEGORIES, null=True, blank=True)
    expense_type = models.CharField(max_length=50, choices=EXPENSE_TYPES, null=True, blank=True)
    vendor = models.CharField(max_length=100, null=True, blank=True)
    receipt_number = models.CharField(max_length=50, null=True, blank=True)

    # Balance fields
    balance_type = models.CharField(max_length=50, choices=BALANCE_TYPES, null=True, blank=True)
    account = models.CharField(max_length=100, null=True, blank=True)

    # Advance fields
    recipient_name = models.CharField(max_length=100, null=True, blank=True)
    recipient_position = models.CharField(max_length=100, null=True, blank=True)
    repayment_deadline = models.DateField(null=True, blank=True)
    repayment_method = models.CharField(max_length=50, null=True, blank=True)

    # Payable fields
    lender_name = models.CharField(max_length=100, null=True, blank=True)
    lender_contact = models.CharField(max_length=100, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)

    # Add new fields for approval tracking
    current_approval_level = models.CharField(max_length=50, choices=(
        ('cashier', 'Cashier Review'),
        ('deputy', 'Deputy Director'),
        ('executive', 'Executive Director'),
        ('ceo', 'CEO'),
    ), default='cashier')
    
    forwarded_to_deputy = models.BooleanField(default=False)
    deputy_approved = models.BooleanField(default=False)
    executive_approved = models.BooleanField(default=False)
    ceo_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} ({self.status})"

    def get_remaining_amount(self):
        """Calculate remaining amount for advance records"""
        if self.transaction_type != 'advance':
            return 0
            
        total_paid = self.paybacks.aggregate(Sum('amount'))['amount__sum'] or 0
        return self.amount - total_paid

    def save(self, *args, **kwargs):
        if not self.reference_number:
            # Get the prefix based on transaction type
            prefix_map = {
                'income': 'INC',
                'expense': 'EXP',
                'advance': 'ADV',
                'balance': 'BAL',
                'payable': 'PAY'
            }
            prefix = prefix_map.get(self.transaction_type, 'REC')
            
            # Get current year and month
            current_date = timezone.now()
            year = current_date.strftime('%Y')
            month = current_date.strftime('%m')
            
            # Get the last record with same prefix and year
            last_record = Record.objects.filter(
                reference_number__startswith=f"{prefix}-{year}"
            ).order_by('reference_number').last()
            
            if last_record:
                # Extract the sequence number from the last record
                try:
                    last_sequence = int(last_record.reference_number.split('-')[-1])
                    new_sequence = str(last_sequence + 1).zfill(4)
                except (ValueError, IndexError):
                    new_sequence = '0001'
            else:
                new_sequence = '0001'
            
            # Generate the reference number
            self.reference_number = f"{prefix}-{year}{month}-{new_sequence}"
        
        super().save(*args, **kwargs)

    def get_approval_status_display(self):
        """Get a user-friendly display of the current approval status"""
        if self.status == 'pending' and not self.forwarded_to_deputy:
            return 'Pending Cashier Review'
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    def can_be_modified(self, user):
        """Check if the record can be modified by the given user"""
        if user.user_type == 'data_entry':
            return False
        if user.user_type == 'cashier':
            return self.status == 'pending' and not self.forwarded_to_deputy
        return user.is_superuser

    def can_approve(self, user):
        """Check if the user can approve the record at their level"""
        if user.user_type == 'deputy_director' and self.status == 'pending_deputy':
            return True
        if user.user_type == 'executive_director' and self.status == 'pending_executive':
            return True
        if user.user_type == 'chief_executive' and self.status == 'pending_ceo':
            return True
        return False


class RecordApproval(models.Model):
    APPROVAL_LEVELS = (
        ('cashier', 'Cashier'),
        ('deputy', 'Deputy Director'),
        ('executive', 'Executive Director'),
        ('ceo', 'CEO'),
    )

    record = models.ForeignKey(Record, on_delete=models.CASCADE, related_name='approvals')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    approval_level = models.CharField(max_length=20, choices=APPROVAL_LEVELS)
    status = models.CharField(max_length=20, choices=Record.STATUS_CHOICES)
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']  # Changed to ascending to show approval flow chronologically
        unique_together = ['record', 'approval_level']  # Ensure one approval per level

    def __str__(self):
        return f"{self.record} - {self.get_approval_level_display()} {self.status}"


class UserActivity(models.Model):
    ACTIVITY_TYPES = (
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('record_create', 'Record Created'),
        ('record_update', 'Record Updated'),
        ('record_delete', 'Record Deleted'),
        ('record_approve', 'Record Approved'),
        ('record_reject', 'Record Rejected'),
        ('profile_update', 'Profile Updated'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField()
    record = models.ForeignKey('Record', on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'User Activities'

    def __str__(self):
        return f"{self.user.username} - {self.activity_type} - {self.created_at}"


class UserSettings(models.Model):
    THEME_CHOICES = (
        ('light', 'Light'),
        ('dark', 'Dark'),
    )
    
    LANGUAGE_CHOICES = (
        ('en', 'English'),
        ('fa', 'Farsi'),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='en')
    notifications_enabled = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    items_per_page = models.IntegerField(default=10)

    class Meta:
        verbose_name_plural = 'User Settings'

    def __str__(self):
        return f"{self.user.username}'s settings"


class TwoFactorAuth(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    secret_key = models.CharField(max_length=32)
    is_enabled = models.BooleanField(default=False)
    backup_codes = models.JSONField(default=list)
    last_used = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"2FA for {self.user.username}"


class AdvancePayback(models.Model):
    PAYMENT_METHODS = (
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('deduction', 'Salary Deduction'),
    )
    
    advance = models.ForeignKey(Record, on_delete=models.CASCADE, related_name='paybacks')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    notes = models.TextField(blank=True)
    is_fully_paid = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"Payback of {self.amount} for {self.advance.reference_number}"

    @property
    def remaining_amount(self):
        total_paid = self.advance.paybacks.aggregate(Sum('amount'))['amount__sum'] or 0
        return self.advance.amount - total_paid
