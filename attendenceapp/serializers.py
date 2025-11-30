from rest_framework import serializers
from .models import AttendanceSettings, AttendanceLog
from django.conf import settings


class AttendanceSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceSettings
        fields = ['start_time', 'end_time', 'late_buffer_minutes']


class AttendanceLogSerializer(serializers.ModelSerializer):
    employee_id = serializers.CharField(source='employee.id', read_only=True)
    name = serializers.CharField(source='employee.get_full_name', read_only=True)
    time = serializers.SerializerMethodField()

    class Meta:
        model = AttendanceLog
        fields = ['id', 'employee_id', 'name', 'time', 'status']

    def get_time(self, obj):
        return obj.checkin_time.strftime('%I:%M %p')
