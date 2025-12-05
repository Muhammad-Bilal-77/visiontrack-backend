from rest_framework import serializers
from .models import SiteSettings, Feature, Step, Employee
from user.models import User
from django.conf import settings


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = "__all__"


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = "__all__"


class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = "__all__"


class EmployeeSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='user.id', read_only=True)
    empId = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email', read_only=True)
    role = serializers.CharField(source='user.role', read_only=True)
    status = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(source='user.date_joined', read_only=True)
    updated_at = serializers.DateTimeField(source='user.date_joined', read_only=True)

    class Meta:
        model = Employee
        fields = ['id', 'empId', 'first_name', 'last_name', 'name', 'email', 'role', 'status', 'photo_url', 'created_at', 'updated_at']

    def get_name(self, obj):
        return obj.name

    def get_status(self, obj):
        return "Active" if obj.user.is_active else "Inactive"

    def get_photo_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class EmployeeCreateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(required=True)
    empId = serializers.CharField(max_length=150, required=True)
    role = serializers.CharField(max_length=10, default='employee')
    photo = serializers.ImageField(required=False, allow_null=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate_empId(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("empId already exists")
        return value

    def create(self, validated_data):
        photo = validated_data.pop('photo', None)
        
        # Create user with employee role
        user = User(
            username=validated_data['empId'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role=User.EMPLOYEE,
            is_active=True
        )
        user.set_password('employee123')  # Default password
        user.save(force_insert=True)  # Skip validation

        # Create employee record
        employee = Employee(user=user)
        if photo:
            employee.image = photo
        employee.save()

        return employee


class EmployeeStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['Active', 'Inactive'], required=True)

    def update(self, instance, validated_data):
        status = validated_data.get('status')
        instance.user.is_active = (status == 'Active')
        instance.user.save()
        return instance
