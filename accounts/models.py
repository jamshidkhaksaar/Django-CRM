from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('client', 'Client'),
        ('data_entry', 'Data Entry'),
        ('cashier', 'Cashier'),
        ('deputy_director', 'Deputy Director'),
        ('executive_director', 'Executive Director'),
        ('chief_executive', 'Chief Executive'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'auth_user'
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return self.username

    def can_approve_records(self):
        return self.user_type in [
            'admin', 'deputy_director', 
            'executive_director', 'chief_executive'
        ]

    def can_edit_record(self):
        return self.user_type in ['admin', 'data_entry']

    def can_delete_record(self):
        return self.user_type == 'admin'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # Additional profile fields

    def __str__(self):
        return f"{self.user.username}'s profile"