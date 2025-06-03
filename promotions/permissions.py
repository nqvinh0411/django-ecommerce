from rest_framework import permissions


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to create, edit or delete objects.
    Regular authenticated users can only view them.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any authenticated request
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions are only allowed to admin users
        return request.user and request.user.is_staff


class CanManagePromotions(permissions.BasePermission):
    """
    Custom permission to only allow users with promotion management permission to edit promotions.
    Staff users have full access, while authenticated users have read-only access.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any authenticated request
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
            
        # Write permissions are only allowed to staff or users with promotions permission
        if request.user and request.user.is_authenticated:
            return request.user.is_staff or hasattr(request.user, 'has_perm') and request.user.has_perm('promotions.manage_promotions')
            
        return False
