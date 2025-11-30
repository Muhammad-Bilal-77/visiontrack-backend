from rest_framework.permissions import BasePermission
from user.models import User


class IsAdminOrSuperUser(BasePermission):
    """Allow access only to authenticated users who are superuser or have role 'admin'."""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if getattr(user, 'is_superuser', False):
            return True

        # fall back to custom role field
        return getattr(user, 'role', None) == User.ADMIN
