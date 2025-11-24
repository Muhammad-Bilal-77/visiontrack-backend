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
    
]
