from rest_framework.permissions import BasePermission, IsAdminUser, SAFE_METHODS


class IsAdminUserForSettings(IsAdminUser):
    """
    Custom permission to only allow admin users to access settings.
    This is a simple extension of IsAdminUser that could be expanded
    with additional logic if needed in the future.
    """
    message = "Only admin users can access system settings."

    def has_permission(self, request, view):
        return super().has_permission(request, view)


class CanManageSettings(BasePermission):
    """
    Custom permission to only allow users with settings management permission to edit system settings.
    Staff users have full access, while authenticated users have read-only access for some settings.
    """
    message = "Only users with settings management permissions can perform this action."
    
    def has_permission(self, request, view):
        # Read permissions are allowed to authenticated users for some views
        if request.method in SAFE_METHODS:
            # For general settings, only admins can view
            if view.__class__.__name__ == 'StoreSettingViewSet':
                return request.user and request.user.is_staff
            # Other settings can be viewed by authenticated users
            return request.user and request.user.is_authenticated
        
        # Write permissions are only allowed to staff or users with settings permission
        if request.user and request.user.is_authenticated:
            return request.user.is_staff or hasattr(request.user, 'has_perm') and request.user.has_perm('settings.manage_settings')
            
        return False
