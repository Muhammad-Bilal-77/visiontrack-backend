from django.db import models
from django.conf import settings
from django.utils import timezone


class AttendanceSettings(models.Model):
    start_time = models.TimeField(default="09:00:00")
    end_time = models.TimeField(default="18:00:00")
    late_buffer_minutes = models.PositiveIntegerField(default=15)

    class Meta:
        verbose_name = 'Attendance Settings'
        verbose_name_plural = 'Attendance Settings'

    def __str__(self):
        return "Global Attendance Settings"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class AttendanceLog(models.Model):
    STATUS_PRESENT = 'present'
    STATUS_LATE = 'late'

    STATUS_CHOICES = (
        (STATUS_PRESENT, 'Present'),
        (STATUS_LATE, 'Late'),
    )

    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    checkin_time = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.employee} - {self.checkin_time} - {self.status}"

    @classmethod
    def create_checkin(cls, employee, checkin_time=None):
        """Create an attendance log and determine late vs present using AttendanceSettings."""
        if checkin_time is None:
            checkin_time = timezone.now()

        settings_obj = AttendanceSettings.get_solo()

        # Build a datetime for today's start time
        start_dt = timezone.datetime.combine(checkin_time.date(), settings_obj.start_time)
        if timezone.is_aware(checkin_time) and timezone.is_naive(start_dt):
            start_dt = timezone.make_aware(start_dt, timezone.get_current_timezone())

        # add buffer
        buffer_delta = timezone.timedelta(minutes=settings_obj.late_buffer_minutes)
        late_threshold = start_dt + buffer_delta

        if checkin_time > late_threshold:
            status = cls.STATUS_LATE
        else:
            status = cls.STATUS_PRESENT

        return cls.objects.create(employee=employee, checkin_time=checkin_time, status=status)
