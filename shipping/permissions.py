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


class IsOrderOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to allow users to view only their own shipments,
    while admins can view all shipments.
    """
    def has_permission(self, request, view):
        # Always require authentication
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Admin can access all
        if request.user.is_staff:
            return True
            
        # For non-admins, only allow safe methods initially
        # and the actual ownership check happens in has_object_permission
        return request.method in permissions.SAFE_METHODS
    
    def has_object_permission(self, request, view, obj):
        # Admin can do anything
        if request.user.is_staff:
            return True
        
        # Check if the user is the owner of the related order
        if hasattr(obj, 'order') and hasattr(obj.order, 'customer') and hasattr(obj.order.customer, 'user'):
            return obj.order.customer.user == request.user
            
        return False


class CanManageShipment(permissions.BasePermission):
    """
    Permission to allow adding tracking info to shipments.
    Admins can add tracking to any shipment, users can't add tracking.
    """
    def has_permission(self, request, view):
        # Only admins can add tracking info
        return request.user and request.user.is_staff