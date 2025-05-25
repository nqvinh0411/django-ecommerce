"""
JWT Authentication Middleware.

Middleware này xử lý việc xác thực JWT cho các requests API, 
giúp đảm bảo tính bảo mật và chuẩn hóa quá trình xác thực
người dùng trong toàn bộ hệ thống e-commerce.
"""
import jwt
import logging
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
from django.utils.functional import SimpleLazyObject
from rest_framework.exceptions import AuthenticationFailed

from core.exceptions.auth import InvalidTokenError, TokenExpiredError, TokenRequiredError

logger = logging.getLogger(__name__)
User = get_user_model()


def get_user_from_token(token):
    """
    Trích xuất thông tin user từ JWT token.
    
    Args:
        token (str): JWT token cần giải mã
        
    Returns:
        User: User object nếu token hợp lệ và user tồn tại
        
    Raises:
        TokenExpiredError: Nếu token đã hết hạn
        InvalidTokenError: Nếu token không hợp lệ
    """
    try:
        # Giải mã JWT token sử dụng SECRET_KEY
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Lấy user ID từ payload
        user_id = payload.get('user_id')
        if not user_id:
            raise InvalidTokenError("Token không chứa user_id")
            
        # Lấy user từ database
        user = User.objects.filter(id=user_id).first()
        if not user:
            raise InvalidTokenError("User không tồn tại")
            
        # Kiểm tra user status (ví dụ: is_active)
        if not user.is_active:
            raise InvalidTokenError("User đã bị vô hiệu hóa")
            
        return user
        
    except jwt.ExpiredSignatureError:
        # Token đã hết hạn
        logger.warning("Expired JWT token attempt")
        raise TokenExpiredError("Token đã hết hạn")
        
    except jwt.InvalidTokenError:
        # Token không hợp lệ (sai chữ ký, etc)
        logger.warning("Invalid JWT token attempt")
        raise InvalidTokenError("Token không hợp lệ")
        
    except Exception as e:
        # Lỗi khác trong quá trình xác thực
        logger.exception("JWT token authentication error: %s", str(e))
        raise InvalidTokenError(f"Lỗi xác thực: {str(e)}")


class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware xác thực JWT cho các requests API.
    
    Middleware này sẽ:
    1. Kiểm tra token trong header Authorization hoặc cookie
    2. Xác thực token và lấy thông tin user
    3. Gắn user vào request để sử dụng trong views
    
    Middleware chỉ xử lý các requests đến API endpoints (/api/),
    và bỏ qua các endpoints không yêu cầu xác thực như login/register.
    
    Nếu token không hợp lệ hoặc hết hạn, request vẫn được xử lý,
    nhưng request.user sẽ là AnonymousUser, và views sẽ quyết định
    xử lý tiếp theo dựa trên permission_classes.
    """
    
    def process_request(self, request):
        """
        Xử lý request trước khi nó đến view.
        
        Args:
            request (HttpRequest): Django request object
            
        Returns:
            None: Middleware không trả về response, chỉ sửa đổi request
        """
        # Chỉ xử lý API requests
        if not request.path.startswith('/api/'):
            return
            
        # Bỏ qua các paths không yêu cầu xác thực (ví dụ: login, register)
        auth_exempt_paths = [
            '/api/v1/auth/login', 
            '/api/v1/auth/register',
            '/api/v1/auth/refresh',
            '/api/v1/auth/password/reset',
            '/api/v1/auth/password/reset/confirm',
        ]
        if any(request.path.startswith(path) for path in auth_exempt_paths):
            return
            
        # Lazy load user để tránh query DB không cần thiết
        request.user = SimpleLazyObject(lambda: self._get_user(request))
        
    def _get_user(self, request):
        """
        Lấy user từ JWT token trong request.
        
        Args:
            request (HttpRequest): Django request object
            
        Returns:
            User: User object nếu token hợp lệ, AnonymousUser nếu không
        """
        # Lấy token từ header Authorization
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        else:
            # Nếu không có Authorization header, thử lấy từ cookie
            token = request.COOKIES.get('access_token', '')
            
        if not token:
            # Không có token, không cần throw exception, để views xử lý permission
            return request.user  # AnonymousUser mặc định
            
        try:
            # Lấy user từ token
            user = get_user_from_token(token)
            return user
        except (TokenExpiredError, InvalidTokenError) as e:
            # Token error, không throw exception, để views xử lý permission
            logger.debug("JWT auth middleware: %s", str(e))
            return request.user  # AnonymousUser mặc định
