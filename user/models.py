from django.db import models
from django.contrib.auth.models import AbstractUser

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

    def __str__(self):
        return self.email