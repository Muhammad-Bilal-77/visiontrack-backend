from django.urls import path
from django.http import JsonResponse
from . import views

def core_index(request):
    return JsonResponse({"message": "Hello from core API!"})

urlpatterns = [
    path('', core_index, name='core_index'),
    path('upload/', views.upload_employee, name='upload_employee'),
    path('success/', views.upload_success, name='upload_success'),
    path('attendance/', views.mark_attendance, name='mark_attendance'),
    path("landing/", views.landing_page_data, name="landing-page-data"),
    
    # Employee Management APIs (specific routes before parameterized ones)
    path('api/employees/', views.EmployeeListCreateView.as_view(), name='employee-list-create'),
    path('api/employees/face-upload/', views.EmployeeFaceUploadView.as_view(), name='employee-face-upload'),
    path('api/employees/check/', views.EmployeeCheckView.as_view(), name='employee-check'),
    path('api/employees/upload/', views.EmployeeFaceUploadView.as_view(), name='employee-upload'),
    path('api/employees/attendance-history/', views.EmployeeAttendanceHistoryView.as_view(), name='employee-attendance-history'),
    path('api/mark-attendance/', views.FaceRecognitionAttendanceView.as_view(), name='face-recognition-attendance'),
    path('api/user-role/', views.UserRoleCheckView.as_view(), name='user-role-check'),
    path('api/employees/<str:pk>/', views.EmployeeDetailView.as_view(), name='employee-detail'),
]
