from rest_framework import permissions


class CreateOnlyPermission(permissions.BasePermission):
    """
    Custom permission cho phép chỉ tạo mới (POST), các hành động khác sẽ bị từ chối.
    """
    message = "Chỉ cho phép tạo mới dữ liệu."

    def has_permission(self, request, view):
        return request.method == 'POST'


class IsAdminUser(permissions.IsAdminUser):
    """
    Allows access only to admin users.
    """
    message = "Bạn cần có quyền quản trị để thực hiện hành động này."


class IsAuthenticated(permissions.IsAuthenticated):
    """
    Allows access only to authenticated users.
    """
    message = "Bạn cần đăng nhập để thực hiện hành động này."


class AllowAny(permissions.AllowAny):
    """
    Allow unrestricted access, regardless of the user being authenticated or not.
    """
    pass


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    The request is authenticated as an admin user, or is a read-only request.
    """
    message = "Chỉ quản trị viên mới có quyền chỉnh sửa."

    def has_permission(self, request, view):
        return bool(
            request.method in permissions.SAFE_METHODS or
            request.user and
            request.user.is_authenticated and
            request.user.is_staff
        )


class IsOwner(permissions.BasePermission):
    """
    Custom permission để chỉ cho phép chủ sở hữu truy cập.
    """
    message = "Bạn không có quyền truy cập đối tượng này."

    def has_object_permission(self, request, view, obj):
        # Kiểm tra nếu user là chủ sở hữu (qua trường 'owner' hoặc 'user')
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """
    message = "Bạn không phải chủ sở hữu của đối tượng này."

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner` or `user`.
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class IsOwnerOrAdminUser(permissions.BasePermission):
    """
    Custom permission: Chỉ cho phép chủ sở hữu hoặc admin truy cập.
    """
    message = "Bạn phải là chủ sở hữu hoặc quản trị viên để thực hiện hành động này."

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        is_owner = False
        if hasattr(obj, 'owner'):
            is_owner = obj.owner == request.user
        elif hasattr(obj, 'user'):
            is_owner = obj.user == request.user

        is_admin = request.user.is_staff

        return is_owner or is_admin
