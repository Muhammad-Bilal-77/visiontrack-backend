from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        # These are the fields your Frontend must send
        fields = ('id', 'email', 'username', 'password', 'first_name', 'last_name', 'phone_number', 'role')