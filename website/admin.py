from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Record

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'user_type', 'department', 'phone', 'is_staff', 'is_active')
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Additional Info', {'fields': ('user_type', 'department', 'phone')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'user_type', 'department', 'phone', 'is_active', 'is_staff'),
        }),
    )
    search_fields = ('username', 'email', 'department')
    ordering = ('username',)

    def save_model(self, request, obj, form, change):
        if obj.is_superuser and obj.user_type != 'superuser':
            obj.user_type = 'superuser'
        super().save_model(request, obj, form, change)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Record)