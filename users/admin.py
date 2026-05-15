from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = ('username', 'email', 'role', 'manager', 'is_active', 'date_joined')
    list_filter  = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('role', 'username')

    fieldsets = UserAdmin.fieldsets + (
        (
            'Team & Role',
            {
                'fields': ('role', 'manager'),
                'description': 'Set the user role and assign a manager (required for employees).'
            }
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('username', 'email', 'role', 'manager', 'password1', 'password2'),
            },
        ),
    )