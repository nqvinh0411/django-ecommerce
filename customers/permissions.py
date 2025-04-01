from rest_framework import permissions

class IsCustomerOwner(permissions.BasePermission):
    """
    Custom permission to only allow customers to edit their own data
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # For customer addresses, check if the customer owns the address
        if hasattr(obj, 'customer'):
            return obj.customer.user == request.user
        
        # For customer object itself
        return obj.user == request.user

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit but allow anyone to read
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff