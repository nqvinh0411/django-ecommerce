from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from datetime import timedelta


def get_tokens_for_user(user):
    """
    Generate JWT tokens for a user.
    Returns a dictionary with access and refresh tokens.
    """
    refresh_token = RefreshToken.for_user(user)
    access_token = refresh_token.access_token
    
    return {
        'refresh': str(refresh_token),
        'access': str(access_token),
    }


def configure_token_settings():
    """
    Configure JWT token settings. Should be called in settings.py.
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
