from rest_framework.permissions import BasePermission, IsAdminUser


class IsAdminUserForSettings(IsAdminUser):
    """
    Custom permission to only allow admin users to access settings.
    This is a simple extension of IsAdminUser that could be expanded
    with additional logic if needed in the future.
    """
    message = "Only admin users can access system settings."

    def has_permission(self, request, view):
        return super().has_permission(request, view)
