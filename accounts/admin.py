from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Transaction

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('User Type', {'fields': ('user_type',)}),
    )

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('amount', 'created_by', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('description', 'created_by__username')

admin.site.register(User, CustomUserAdmin)
admin.site.register(Transaction, TransactionAdmin)
