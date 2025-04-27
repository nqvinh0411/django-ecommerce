from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from datetime import timedelta


def get_tokens_for_user(user):
    """
    Generate JWT tokens for a user.
    
    Tạo access và refresh tokens cho một người dùng sử dụng SimpleJWT.
    Hàm này là wrapper tiện lợi quanh RefreshToken.for_user() để đảm bảo
    tính nhất quán trong việc tạo token trên toàn hệ thống.
    
    Args:
        user (User): Đối tượng User cần tạo token
        
    Returns:
        dict: Dictionary chứa refresh và access tokens dưới dạng string:
            {
                'refresh': str,  # Refresh token dùng để lấy access token mới
                'access': str,   # Access token dùng để xác thực API requests
            }
            
    Example:
        ```python
        from django.contrib.auth import get_user_model
        from core.authentication.tokens import get_tokens_for_user
        
        User = get_user_model()
        user = User.objects.get(email='user@example.com')
        tokens = get_tokens_for_user(user)
        
        # Sử dụng tokens
        access_token = tokens['access']
        refresh_token = tokens['refresh']
        ```
    """
    refresh_token = RefreshToken.for_user(user)
    access_token = refresh_token.access_token
    
    return {
        'refresh': str(refresh_token),
        'access': str(access_token),
    }


def configure_token_settings():
    """
    Configure JWT token settings for SimpleJWT integration.
    
    Hàm này trả về một dictionary cấu hình cho SIMPLE_JWT, thường được
    sử dụng trong settings.py để đảm bảo cấu hình token nhất quán.
    
    Các thiết lập chính:
    - Access token có hiệu lực trong 60 phút
    - Refresh token có hiệu lực trong 7 ngày
    - Refresh tokens được quay vòng khi sử dụng
    - Tokens cũ bị đưa vào blacklist sau khi quay vòng
    
    Returns:
        dict: Dictionary cấu hình đầy đủ cho SIMPLE_JWT setting
        
    Example:
        ```python
        # Trong settings.py
        from core.authentication.tokens import configure_token_settings
        
        SIMPLE_JWT = configure_token_settings()
        ```
        
    Note:
        Các thời gian sống (lifetime) có thể điều chỉnh thông qua tham số
        trong hàm này. Mặc định được thiết lập cho ứng dụng e-commerce
        với cân bằng giữa bảo mật và trải nghiệm người dùng.
    """
    return {
        'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
        'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
        'ROTATE_REFRESH_TOKENS': True,
        'BLACKLIST_AFTER_ROTATION': True,
        'ALGORITHM': 'HS256',
        'SIGNING_KEY': settings.SECRET_KEY,
        'VERIFYING_KEY': None,
        'AUTH_HEADER_TYPES': ('Bearer',),
        'USER_ID_FIELD': 'id',
        'USER_ID_CLAIM': 'user_id',
        'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
        'TOKEN_TYPE_CLAIM': 'token_type',
        'JTI_CLAIM': 'jti',
        'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
        'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
        'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
    }
