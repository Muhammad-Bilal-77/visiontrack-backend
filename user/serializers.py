from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        # These are the fields your Frontend must send
        fields = ('id', 'email', 'username', 'password', 'first_name', 'last_name', 'phone_number', 'role')
    
    def validate_role(self, value):
        """Prevent direct creation of employee users via API."""
        if value == User.EMPLOYEE:
            raise serializers.ValidationError(
                'Cannot create users with employee role directly. '
                'Employees must be created through the Employee model in the core app.'
            )
        return value

class UserSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'phone_number', 'role')
        read_only_fields = ('id', 'email')