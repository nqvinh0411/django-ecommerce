from rest_framework import permissions


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to edit, but allow read-only for authenticated users.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any authenticated request
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        # Write permissions are only allowed to admin users
        return request.user and request.user.is_staff


class CreateOnlyPermission(permissions.BasePermission):
    """
    Custom permission that only allows creation of new objects, but not edit or delete.
    """
    def has_permission(self, request, view):
        # Allow GET for listing and detail view
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
            
        # Only allow POST (create)
        if request.method == 'POST':
            return request.user and request.user.is_authenticated
            
        # Deny all other methods
        return False