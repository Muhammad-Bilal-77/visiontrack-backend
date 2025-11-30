from django.urls import path
from . import views

urlpatterns = [
    path('config/', views.AttendanceConfigView.as_view(), name='attendance-config'),
    path('stats/summary/', views.SummaryStatsView.as_view(), name='attendance-summary'),
    path('stats/daily/', views.DailyStatsView.as_view(), name='attendance-daily'),
    path('stats/employees/', views.EmployeeStatsView.as_view(), name='attendance-employees'),
    path('logs/today/', views.TodayLogsView.as_view(), name='attendance-today-logs'),
    path('notify/', views.NotifyView.as_view(), name='attendance-notify'),
]
