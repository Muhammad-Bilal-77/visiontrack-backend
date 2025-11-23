from django.urls import path
from django.http import JsonResponse

def core_index(request):
    return JsonResponse({"message": "Hello from core API!"})

urlpatterns = [
    path('', core_index, name='core_index'),
]
