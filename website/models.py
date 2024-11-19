from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
from django.urls import reverse
from accounts.models import Transaction
from django.contrib.auth.models import User
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Adds additional fields for user type, department, and phone.
    """
    USER_TYPE_CHOICES = [
        ('superuser', 'Superuser'),
        ('data_entry', 'Data Entry'),
        ('deputy_director', 'Deputy Executive Director'),
        ('executive_director', 'Executive Director'),
        ('chief_executive', 'Chief Executive Director'),
    ]
    
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='data_entry'
    )
    department = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='website_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='website_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return f"{self.username} - {self.get_user_type_display()}"

    def has_menu_permission(self):
        if self.is_superuser:
            return [
                'home',
                'all_records',
                'user_management',
                'add_record',
                'dashboard',
                'approval',
                'edit_record',
                'delete_record',
                'pending_records',
                'approved_records',
                'rejected_records'
            ]
            
        menu_permissions = {
            'superuser': [
                'home',
                'all_records',
                'user_management',
                'add_record',
                'dashboard',
                'approval',
                'edit_record',
                'delete_record'
            ],
            'data_entry': [
                'home',
                'all_records', 
                'add_record', 
                'dashboard',
                'edit_record'
            ],
            'deputy_director': [
                'home',
                'all_records', 
                'dashboard', 
                'approval',
                'pending_records',
                'approved_records',
                'rejected_records'
            ],
            'executive_director': [
                'home',
                'all_records', 
                'dashboard', 
                'approval',
                'pending_records',
                'approved_records',
                'rejected_records'
            ],
            'chief_executive': [
                'home',
                'all_records', 
                'dashboard', 
                'approval',
                'pending_records',
                'approved_records',
                'rejected_records'
            ]
        }
        return menu_permissions.get(self.user_type, [])

    def has_record_permission(self, action):
        permissions = {
            'superadmin': ['view', 'add', 'edit', 'delete', 'approve'],
            'data_entry': ['view', 'add', 'edit'],
            'deputy_director': ['view', 'approve'],
            'executive_director': ['view', 'approve'],
            'chief_executive': ['view', 'approve']
        }
        return action in permissions.get(self.user_type, [])

    def get_approval_stage(self):
        stages = {
            'deputy_director': 'pending_deputy',
            'executive_director': 'pending_executive',
            'chief_executive': 'final_approval'
        }
        return stages.get(self.user_type)

    def can_manage_users(self):
        return self.user_type == 'superadmin'

    def can_approve_records(self):
        return self.user_type in ['deputy_director', 'executive_director', 'chief_executive']

    def can_view_user_management(self):
        return self.user_type == 'superadmin'

    def can_edit_record(self):
        return self.user_type in ['superadmin', 'data_entry']

    def can_delete_record(self):
        return self.user_type == 'superadmin'

    def get_approval_level(self):
        levels = {
            'deputy_director': 1,
            'executive_director': 2,
            'chief_executive': 3
        }
        return levels.get(self.user_type, 0)

    def notify_approval_status(self, approver, status, comments):
        notification_mapping = {
            'deputy_director': ['data_entry'],
            'executive_director': ['data_entry', 'deputy_director'],
            'chief_executive': ['data_entry', 'deputy_director', 'executive_director']
        }
        
        users_to_notify = CustomUser.objects.filter(
            user_type__in=notification_mapping.get(approver.user_type, [])
        )
        
        for user in users_to_notify:
            Notification.objects.create(
                user=user,
                record=self,
                message=f"Record {self.id} has been {status} by {approver.get_user_type_display()}. Comments: {comments}",
                notification_type='approval'
            )

class Record(models.Model):
    """
    Model representing a transaction record.
    Contains various fields to capture transaction details.
    """
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('advance', 'Advance'),
    ]
    
    APPROVAL_STATUS_CHOICES = [
        ('pending_deputy', 'Pending Deputy Director Approval'),
        ('pending_executive', 'Pending Executive Director Approval'),
        ('pending_chief', 'Pending Chief Executive Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]
    
    REVIEWER_RESULT_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    item_name = models.CharField(max_length=100)
    item_type = models.CharField(max_length=100)
    description = models.TextField()
    project = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    requester = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='requested_records')
    reviewer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviewed_records')
    unit_measure = models.CharField(max_length=50)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_value = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    comments = models.TextField(blank=True)
    
    # Approval workflow fields
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default='pending_deputy'
    )
    
    reviewer_result = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected')
        ],
        default='pending'
    )
    
    approval_history = models.JSONField(default=list)
    deputy_director_approval = models.BooleanField(default=False)
    deputy_director_comments = models.TextField(blank=True)
    executive_director_approval = models.BooleanField(default=False)
    executive_director_comments = models.TextField(blank=True)
    chief_executive_approval = models.BooleanField(default=False)
    chief_executive_comments = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    CASHIER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    cashier_status = models.CharField(max_length=50, default='pending')

    def notify_users(self, title, message):
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        channel_layer = get_channel_layer()
        
        users_to_notify = set()
        if self.requester:
            users_to_notify.add(self.requester)
        
        users_to_notify.update(CustomUser.objects.filter(user_type='superadmin'))
        
        status_to_notify = {
            'pending_deputy': 'deputy_director',
            'pending_executive': 'executive_director',
            'pending_chief': 'chief_executive'
        }
        
        if self.approval_status in status_to_notify:
            users_to_notify.update(
                CustomUser.objects.filter(user_type=status_to_notify[self.approval_status])
            )
        
        notifications = []
        for user in users_to_notify:
            notification = Notification.objects.create(
                user=user,
                record=self,
                title=title,
                message=message,
                notification_type='approval'
            )
            notifications.append(notification)
            
            # Send WebSocket notification
            async_to_sync(channel_layer.group_send)(
                f"user_{user.id}_notifications",
                {
                    "type": "notify",
                    "message": {
                        "id": notification.id,
                        "title": title,
                        "message": message,
                        "record_id": self.id,
                        "created_at": notification.created_at.isoformat()
                    }
                }
            )

    def save(self, *args, **kwargs):
        is_new = not self.pk
        old_status = self.approval_status if self.pk else None
        
        if is_new:
            # Set default values for new records
            self.approval_status = 'pending_deputy'
            self.approval_history = []
            self.deputy_director_approval = False
            self.executive_director_approval = False
            self.chief_executive_approval = False
            self.deputy_director_comments = ''
            self.executive_director_comments = ''
            self.chief_executive_comments = ''
        
        super().save(*args, **kwargs)
        
        # Send notifications based on status changes
        if is_new:
            self.notify_users(
                'New Record Created',
                f'Record #{self.pk} has been created and is pending Deputy Director approval'
            )
        elif old_status != self.approval_status:
            status_messages = {
                'pending_executive': 'is now pending Executive Director approval',
                'pending_chief': 'is now pending Chief Executive approval',
                'approved': 'has been fully approved',
                'rejected': 'has been rejected'
            }
            if self.approval_status in status_messages:
                self.notify_users(
                    'Record Status Updated',
                    f'Record #{self.pk} {status_messages[self.approval_status]}'
                )

    def __str__(self):
        return f"{self.transaction_type} - {self.item_name}"

    def get_absolute_url(self):
        return reverse('edit_record', args=[str(self.id)])

    def create_notification(self, message):
        user_types = ['data_entry', 'deputy_director', 'executive_director', 'chief_executive']
        users = CustomUser.objects.filter(user_type__in=user_types)
        for user in users:
            Notification.objects.create(user=user, message=message)

    def get_next_approver_type(self):
        approval_flow = {
            'pending_deputy': 'Deputy Director',
            'pending_executive': 'Executive Director',
            'pending_chief': 'Chief Executive'
        }
        return approval_flow.get(self.approval_status, None)

    def get_approval_status_label(self):
        if self.approval_status == 'approved':
            return 'Fully Approved'
        elif self.approval_status == 'rejected':
            return 'Rejected'
        else:
            return f'Awaiting {self.get_next_approver_type()} Approval'

    def get_approval_history(self):
        history = []
        if self.deputy_approval:
            history.append({
                'role': 'Deputy Director',
                'approver': self.deputy_approval,
                'date': self.deputy_approval_date,
                'comments': self.deputy_comments
            })
        if self.executive_approval:
            history.append({
                'role': 'Executive Director',
                'approver': self.executive_approval,
                'date': self.executive_approval_date,
                'comments': self.executive_comments
            })
        if self.chief_approval:
            history.append({
                'role': 'Chief Executive',
                'approver': self.chief_approval,
                'date': self.chief_approval_date,
                'comments': self.chief_comments
            })
        return history

    def can_be_approved_by(self, user):
        approval_stages = {
            'pending_deputy': 'deputy_director',
            'pending_executive': 'executive_director',
            'pending_chief': 'chief_executive'
        }
        return user.user_type == approval_stages.get(self.approval_status)

    def process_approval(self, user, status, comments):
        approval_flow = {
            'deputy_director': {
                'approved': 'pending_executive',
                'field': 'deputy_director_approval',
                'comments_field': 'deputy_director_comments',
                'next_approver': 'Executive Director'
            },
            'executive_director': {
                'approved': 'pending_chief',
                'field': 'executive_director_approval',
                'comments_field': 'executive_director_comments',
                'next_approver': 'Chief Executive'
            },
            'chief_executive': {
                'approved': 'approved',
                'field': 'chief_executive_approval',
                'comments_field': 'chief_executive_comments',
                'next_approver': None
            }
        }
        
        if user.user_type not in approval_flow:
            raise ValueError("Invalid approver type")
            
        flow = approval_flow[user.user_type]
        
        # Set approval fields
        setattr(self, flow['field'], True if status == 'approved' else False)
        setattr(self, flow['comments_field'], comments)
        
        # Update approval history
        approval_entry = {
            'user': user.id,
            'role': user.user_type,
            'status': status,
            'comments': comments,
            'date': timezone.now().isoformat()
        }
        
        if not self.approval_history:
            self.approval_history = []
        self.approval_history.append(approval_entry)
        
        # Update approval status
        if status == 'approved':
            self.approval_status = flow['approved']
        elif status == 'rejected':
            self.approval_status = 'rejected'
        
        self.save()

    def process_final_approval(self):
        if self.chief_executive_approval:
            # Update budget calculations
            if self.transaction_type == 'income':
                Budget.objects.create(
                    record=self,
                    amount=self.total_value,
                    transaction_type='income'
                )
            elif self.transaction_type in ['expense', 'advance']:
                Budget.objects.create(
                    record=self,
                    amount=-self.total_value,
                    transaction_type=self.transaction_type
                )

class DefaultChoices(models.Model):
    item_types = models.JSONField(default=list)
    projects = models.JSONField(default=list)
    locations = models.JSONField(default=list)
    unit_measures = models.JSONField(default=list)
    reviewers = models.JSONField(default=list)

    def __str__(self):
        return "Default Choices"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('approval', 'Approval Status Change'),
        ('comment', 'New Comment'),
        ('record', 'Record Update')
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    record = models.ForeignKey(Record, on_delete=models.CASCADE, related_name='notifications')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    @classmethod
    def notify_all(cls, record, notification_type, title, message):
        users_to_notify = CustomUser.objects.filter(
            user_type__in=['data_entry', 'deputy_director', 'executive_director', 'chief_executive']
        )
        notifications = [
            cls(
                user=user,
                notification_type=notification_type,
                title=title,
                message=message,
                record=record
            ) for user in users_to_notify
        ]
        cls.objects.bulk_create(notifications)

    def save(self, *args, **kwargs):
        is_new = not self.pk
        super().save(*args, **kwargs)
        
        if is_new:
            # Send real-time notification
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{self.user.id}",
                {
                    "type": "notification.message",
                    "message": {
                        "id": self.id,
                        "title": self.title,
                        "message": self.message,
                        "created_at": self.created_at.isoformat(),
                        "is_read": self.is_read
                    }
                }
            )

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Add any additional fields you need
    
    def __str__(self):
        return f"{self.user.username}'s profile"