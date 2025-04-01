from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAdminUser


class IsAdminUserForReports(IsAdminUser):
    """
    Custom permission to only allow admin users to access reports.
    This is a simple extension of IsAdminUser that could be expanded
    with additional logic if needed in the future.
    """
    message = "Only admin users can access reports."

    def has_permission(self, request, view):
        return super().has_permission(request, view)
