from django.urls import path
from django.http import JsonResponse

def user_index(request):
    return JsonResponse({"message": "Hello from user API!"})

urlpatterns = [
    path('', user_index, name='user_index'),
]
