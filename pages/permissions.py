from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAdminUser


class IsAdminUserOrReadOnly(BasePermission):
    """
    Custom permission to only allow admin users to edit, but anyone to view.
    """
    message = "Only admin users can modify content."

    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in SAFE_METHODS:
            return True
            
        # Write permissions are only allowed to admin users
        return bool(request.user and request.user.is_staff)
