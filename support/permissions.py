from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to allow:
    - Admin users to see and modify all tickets
    - Regular users to see and modify only their own tickets
    """
    
    def has_permission(self, request, view):
        # Allow authenticated users
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Admin can do anything
        if request.user.is_staff:
            return True
            
        # Check if the ticket belongs to the requesting user
        if hasattr(obj, 'customer'):
            return obj.customer.user == request.user
        elif hasattr(obj, 'ticket'):
            # For replies, check the parent ticket
            return obj.ticket.customer.user == request.user
        return False


class IsAdminUser(permissions.BasePermission):
    """
    Permission to only allow admin users access.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff
