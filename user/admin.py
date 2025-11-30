from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser')
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('phone_number', 'role')}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('email', 'phone_number', 'role', 'first_name', 'last_name')}),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        """Limit role choices to exclude employee for new users."""
        form = super().get_form(request, obj, **kwargs)
        if 'role' in form.base_fields and not obj:  # Only for new users
            # Filter out employee role
            form.base_fields['role'].choices = [
                choice for choice in User.ROLE_CHOICES 
                if choice[0] != User.EMPLOYEE
            ]
            form.base_fields['role'].help_text = 'Employee users must be created through the Employee model in the core app.'
        return form
