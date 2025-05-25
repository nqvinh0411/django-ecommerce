"""
Authentication Exceptions.

Module này định nghĩa các exception chuyên biệt cho việc xử lý lỗi xác thực
trong hệ thống API, bao gồm JWT, OAuth và các phương thức xác thực khác.
"""

from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status


class TokenRequiredError(AuthenticationFailed):
    """
    Exception khi token xác thực không được cung cấp.
    
    Sử dụng exception này khi API endpoint yêu cầu token
    nhưng không tìm thấy trong request.
    
    Attributes:
        status_code: HTTP 401 Unauthorized
        default_detail: Thông báo mặc định cho người dùng
        default_code: Mã lỗi để xác định loại exception
    """
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Token xác thực không được cung cấp.'
    default_code = 'token_required'


class InvalidTokenError(AuthenticationFailed):
    """
    Exception khi token xác thực không hợp lệ.
    
    Sử dụng exception này khi token có định dạng không hợp lệ,
    chữ ký không đúng, hoặc nội dung không hợp lệ.
    
    Attributes:
        status_code: HTTP 401 Unauthorized
        default_detail: Thông báo mặc định cho người dùng
        default_code: Mã lỗi để xác định loại exception
    """
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Token xác thực không hợp lệ.'
    default_code = 'invalid_token'


class TokenExpiredError(AuthenticationFailed):
    """
    Exception khi token xác thực đã hết hạn.
    
    Sử dụng exception này khi token hợp lệ nhưng đã hết hạn,
    yêu cầu người dùng làm mới token hoặc đăng nhập lại.
    
    Attributes:
        status_code: HTTP 401 Unauthorized
        default_detail: Thông báo mặc định cho người dùng
        default_code: Mã lỗi để xác định loại exception
    """
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Token xác thực đã hết hạn.'
    default_code = 'token_expired'


class InsufficientScopeError(AuthenticationFailed):
    """
    Exception khi token không có đủ quyền truy cập.
    
    Sử dụng exception này khi token hợp lệ nhưng không có scope
    hoặc permission cần thiết để truy cập resource.
    
    Attributes:
        status_code: HTTP 403 Forbidden
        default_detail: Thông báo mặc định cho người dùng
        default_code: Mã lỗi để xác định loại exception
    """
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Token không có đủ quyền truy cập.'
    default_code = 'insufficient_scope'


class AccountDisabledError(AuthenticationFailed):
    """
    Exception khi tài khoản người dùng đã bị vô hiệu hóa.
    
    Sử dụng exception này khi token hợp lệ nhưng tài khoản
    đã bị vô hiệu hóa hoặc tạm khóa.
    
    Attributes:
        status_code: HTTP 403 Forbidden
        default_detail: Thông báo mặc định cho người dùng
        default_code: Mã lỗi để xác định loại exception
    """
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Tài khoản đã bị vô hiệu hóa.'
    default_code = 'account_disabled'
