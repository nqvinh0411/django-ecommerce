"""
Authentication helpers for microservice communication
"""

import logging
import time
import jwt
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class JWTTokenProvider:
    """Provides JWT tokens for microservice authentication"""
    
    def __init__(self, secret_key=None, issuer=None, audience=None, 
                 expires_in=3600, refresh_threshold=300):
        """
        Initialize the JWT token provider
        
        Args:
            secret_key: JWT secret key (defaults to settings)
            issuer: Token issuer (defaults to settings)
            audience: Token audience (defaults to settings)
            expires_in: Token expiration time in seconds
            refresh_threshold: Time in seconds before expiration to refresh
        """
        self.secret_key = secret_key or getattr(
            settings, 'MICROSERVICE_JWT_SECRET_KEY', None
        )
        self.issuer = issuer or getattr(
            settings, 'MICROSERVICE_JWT_ISSUER', 'e_commerce'
        )
        self.audience = audience
        self.expires_in = expires_in
        self.refresh_threshold = refresh_threshold
        self._token = None
        self._token_expiry = None
    
    def get_token(self):
        """
        Get a valid JWT token, creating or refreshing if necessary
        
        Returns:
            JWT token string
        """
        # Check if we need to create or refresh the token
        if self._should_refresh_token():
            self._refresh_token()
        
        return self._token
    
    def _should_refresh_token(self):
        """Check if the token needs to be refreshed"""
        if not self._token or not self._token_expiry:
            return True
        
        # Check if token is close to expiration
        now = timezone.now().timestamp()
        return now > (self._token_expiry - self.refresh_threshold)
    
    def _refresh_token(self):
        """Create a new JWT token"""
        if not self.secret_key:
            logger.warning("No JWT secret key configured for microservice authentication")
            self._token = None
            self._token_expiry = None
            return
        
        now = timezone.now().timestamp()
        expiry = now + self.expires_in
        
        # Create token payload
        payload = {
            'iss': self.issuer,
            'iat': now,
            'exp': expiry,
            'service': 'e_commerce',
        }
        
        # Add audience if specified
        if self.audience:
            payload['aud'] = self.audience
        
        try:
            # Create and sign the token
            self._token = jwt.encode(
                payload,
                self.secret_key,
                algorithm='HS256'
            )
            self._token_expiry = expiry
            
        except Exception as e:
            logger.error(f"Failed to create JWT token: {str(e)}")
            self._token = None
            self._token_expiry = None
    
    def __call__(self):
        """Make the object callable to get a token"""
        return self.get_token()


def get_default_token_provider(service_name=None):
    """
    Get a default token provider for a service
    
    Args:
        service_name: Name of the service (for audience)
    
    Returns:
        JWTTokenProvider instance
    """
    # Get service-specific settings if available
    secret_key = getattr(
        settings, 
        f"{service_name.upper()}_JWT_SECRET_KEY" if service_name else "MICROSERVICE_JWT_SECRET_KEY", 
        getattr(settings, "MICROSERVICE_JWT_SECRET_KEY", None)
    )
    
    audience = service_name
    
    return JWTTokenProvider(
        secret_key=secret_key,
        audience=audience
    )
