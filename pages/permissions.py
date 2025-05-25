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


class CanManagePages(BasePermission):
    """
    Custom permission to only allow users with page management permission to edit pages.
    Staff users have full access, while authenticated users have read-only access.
    """
    message = "Only users with page management permissions can perform this action."
    
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in SAFE_METHODS:
            return True
            
        # Write permissions are only allowed to staff or users with page management permission
        if request.user and request.user.is_authenticated:
            return request.user.is_staff or hasattr(request.user, 'has_perm') and request.user.has_perm('pages.manage_pages')
            
        return False
