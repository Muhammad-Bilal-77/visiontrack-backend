from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .permissions import IsAdminOrSuperUser
from django.utils import timezone
from django.db.models import Count
from django.conf import settings
from django.core.mail import send_mail

from .models import AttendanceSettings, AttendanceLog
from .serializers import AttendanceSettingsSerializer, AttendanceLogSerializer
from user.models import User

import calendar
from datetime import datetime, timedelta, date


class AttendanceConfigView(APIView):
    permission_classes = [IsAdminOrSuperUser]

    def get(self, request):
        cfg = AttendanceSettings.get_solo()
        serializer = AttendanceSettingsSerializer(cfg)
        return Response(serializer.data)

    def post(self, request):
        cfg = AttendanceSettings.get_solo()
        serializer = AttendanceSettingsSerializer(cfg, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class SummaryStatsView(APIView):
    permission_classes = [IsAdminOrSuperUser]

    def get(self, request):
        month = request.query_params.get('month')
        today = timezone.localdate()
        if month:
            try:
                month = int(month)
            except ValueError:
                month = today.month
        else:
            month = today.month

        total_employees = User.objects.filter(role=User.EMPLOYEE).count()

        # today's stats
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())

        present_today = AttendanceLog.objects.filter(checkin_time__date=today, status=AttendanceLog.STATUS_PRESENT).count()
        late_today = AttendanceLog.objects.filter(checkin_time__date=today, status=AttendanceLog.STATUS_LATE).count()
        absent_today = max(0, total_employees - (present_today + late_today))

        # monthly percentages for pie chart: use counts for month (present vs late vs absent)
        month_start = date(today.year, month, 1)
        last_day = calendar.monthrange(today.year, month)[1]
        month_end = date(today.year, month, last_day)

        month_present = AttendanceLog.objects.filter(checkin_time__date__range=(month_start, month_end), status=AttendanceLog.STATUS_PRESENT).count()
        month_late = AttendanceLog.objects.filter(checkin_time__date__range=(month_start, month_end), status=AttendanceLog.STATUS_LATE).count()

        # For pie-chart we calculate ratios by logs (not by days); if there are no logs, avoid division by zero
        total_logs = month_present + month_late
        if total_logs == 0:
            present_pct = 0
            late_pct = 0
            absent_pct = 100
        else:
            present_pct = round((month_present / total_logs) * 100)
            late_pct = round((month_late / total_logs) * 100)
            absent_pct = max(0, 100 - (present_pct + late_pct))

        data = {
            "cards": {
                "total_employees": total_employees,
                "present_today": present_today,
                "late_today": late_today,
                "absent_today": absent_today,
            },
            "pie_chart": [
                {"name": "Present", "value": present_pct, "color": "#22c55e"},
                {"name": "Late", "value": late_pct, "color": "#eab308"},
                {"name": "Absent", "value": absent_pct, "color": "#ef4444"},
            ]
        }

        return Response(data)


class DailyStatsView(APIView):
    permission_classes = [IsAdminOrSuperUser]

    def get(self, request):
        today = timezone.localdate()
        days = []
        for delta in range(6, -1, -1):
            d = today - timedelta(days=delta)
            weekday_name = d.strftime('%a')
            present = AttendanceLog.objects.filter(checkin_time__date=d, status=AttendanceLog.STATUS_PRESENT).count()
            late = AttendanceLog.objects.filter(checkin_time__date=d, status=AttendanceLog.STATUS_LATE).count()
            total_employees = User.objects.filter(role=User.EMPLOYEE).count()
            absent = max(0, total_employees - (present + late))
            days.append({"name": weekday_name, "present": present, "late": late, "absent": absent})

        return Response(days)


class EmployeeStatsView(APIView):
    permission_classes = [IsAdminOrSuperUser]

    def get(self, request):
        # current month from 1st to today
        today = timezone.localdate()
        month_start = date(today.year, today.month, 1)
        month_end = today

        users = User.objects.filter(role=User.EMPLOYEE)
        result = []
        # compute working days so far (weekdays)
        total_working_days = 0
        d = month_start
        while d <= month_end:
            if d.weekday() < 5:
                total_working_days += 1
            d += timedelta(days=1)

        for u in users:
            present = AttendanceLog.objects.filter(employee=u, checkin_time__date__range=(month_start, month_end), status=AttendanceLog.STATUS_PRESENT).count()
            late = AttendanceLog.objects.filter(employee=u, checkin_time__date__range=(month_start, month_end), status=AttendanceLog.STATUS_LATE).count()
            absent = max(0, total_working_days - (present + late))
            result.append({
                "id": str(u.id),
                "name": u.get_full_name() or u.email,
                "present": present,
                "late": late,
                "absent": absent,
            })

        return Response(result)


class TodayLogsView(APIView):
    permission_classes = [IsAdminOrSuperUser]

    def get(self, request):
        today = timezone.localdate()
        logs = AttendanceLog.objects.filter(checkin_time__date=today).order_by('-checkin_time')[:200]
        serializer = AttendanceLogSerializer(logs, many=True)
        return Response(serializer.data)


class NotifyView(APIView):
    permission_classes = [IsAdminOrSuperUser]

    def post(self, request):
        employee_id = request.data.get('employee_id')
        message_type = request.data.get('message_type')

        try:
            user = User.objects.get(id=employee_id)
        except User.DoesNotExist:
            return Response({"detail": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

        # simple mapping for message types
        if message_type == 'late_warning':
            subject = 'Late Attendance Notice'
            message = 'You were late today. Please be on time.'
        else:
            subject = 'Notification'
            message = 'You have a new notification.'

        # send email (may require valid email settings)
        try:
            send_mail(subject, message, None, [user.email], fail_silently=False)
            return Response({"message": f"Email sent to {user.email}"})
        except Exception as e:
            return Response({"message": f"Failed to send email: {str(e)}"}, status=500)
