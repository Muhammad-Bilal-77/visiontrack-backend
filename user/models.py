from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

class User(AbstractUser):
    # 1. Define Roles
    ADMIN = 'admin'
    EMPLOYEE = 'employee'
    
    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (EMPLOYEE, 'Employee'),
    )
    
    # 2. Custom Fields
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=EMPLOYEE)

    # 3. Make Email the Login Field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'phone_number', 'role']

    def clean(self):
        """Prevent direct creation of employee users. Employees must be created through Employee model in core app."""
        super().clean()
        # Only validate on creation (when pk is None)
        if not self.pk and self.role == self.EMPLOYEE:
            raise ValidationError({'role': 'Cannot directly create users with employee role. Employees must be created through the Employee model in the core app.'})

    def save(self, *args, **kwargs):
        # Run validation before save (only for new users)
        # Skip validation if force_insert=True (for management commands/bulk operations)
        if not self.pk and not kwargs.get('force_insert', False):
            self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email