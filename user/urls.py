from django.urls import path
from .views import verify

urlpatterns = [
    path('auth/verify/', verify, name='auth_verify'),
]
