from django.contrib import admin
from .models import AttendanceSettings, AttendanceLog


@admin.register(AttendanceSettings)
class AttendanceSettingsAdmin(admin.ModelAdmin):
    list_display = ('start_time', 'end_time', 'late_buffer_minutes')


@admin.register(AttendanceLog)
class AttendanceLogAdmin(admin.ModelAdmin):
    list_display = ('employee', 'checkin_time', 'status')
    list_filter = ('status', 'checkin_time')
