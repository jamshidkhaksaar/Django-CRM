from django.contrib import admin
from .models import Transaction

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('amount', 'created_by', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('description', 'created_by__username')

admin.site.register(Transaction, TransactionAdmin)
