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


class CanManageInventory(permissions.BasePermission):
    """
    Custom permission to only allow users with inventory management permission to edit inventory items.
    Staff users have full access, while authenticated users have read-only access.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any authenticated request
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
            
        # Write permissions are only allowed to staff or users with inventory permission
        if request.user and request.user.is_authenticated:
            return request.user.is_staff or hasattr(request.user, 'has_perm') and request.user.has_perm('inventory.manage_inventory')
            
        return False