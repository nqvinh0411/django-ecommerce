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


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of a voucher to view it.
    Admin users can view all vouchers.
    """
    def has_permission(self, request, view):
        # Always require authentication
        return request.user and request.user.is_authenticated
        
    def has_object_permission(self, request, view, obj):
        # Admin can do anything
        if request.user.is_staff:
            return True
        
        # Check if the user is the owner of the voucher
        if hasattr(request.user, 'customer'):
            return obj.owner == request.user.customer
            
        return False
