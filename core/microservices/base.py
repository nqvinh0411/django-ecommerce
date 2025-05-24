"""
Base classes for microservice clients
"""

import logging
import time
import grpc
from django.conf import settings
from .exceptions import ServiceUnavailableError, ServiceTimeoutError

logger = logging.getLogger(__name__)


class BaseMicroserviceClient:
    """Base class for all microservice gRPC clients"""
    
    def __init__(self, service_name, host=None, port=None, timeout=10, secure=False):
        """
        Initialize the microservice client
        
        Args:
            service_name: Name of the microservice
            host: Host address (defaults to settings)
            port: Port number (defaults to settings)
            timeout: Default timeout in seconds
            secure: Whether to use secure connection
        """
        self.service_name = service_name
        self.host = host or getattr(settings, f"{service_name.upper()}_HOST", "localhost")
        self.port = port or getattr(settings, f"{service_name.upper()}_PORT", 50051)
        self.timeout = timeout
        self.secure = secure
        self.channel = None
        self._connect()
    
    def _connect(self):
        """Establish gRPC channel connection"""
        target = f"{self.host}:{self.port}"
        
        try:
            if self.secure:
                # Create secure channel with credentials
                credentials = grpc.ssl_channel_credentials()
                self.channel = grpc.secure_channel(target, credentials)
            else:
                # Create insecure channel for development
                self.channel = grpc.insecure_channel(target)
                
            # Add interceptors for logging, metrics, etc.
            self.channel = grpc.intercept_channel(
                self.channel,
                *self._get_interceptors()
            )
            
            logger.info(f"Connected to {self.service_name} at {target}")
            
        except Exception as e:
            logger.error(f"Failed to connect to {self.service_name}: {str(e)}")
            raise ServiceUnavailableError(f"Cannot connect to {self.service_name}")
    
    def _get_interceptors(self):
        """Get channel interceptors"""
        # Can be extended in subclasses
        return []
    
    def close(self):
        """Close the gRPC channel"""
        if self.channel:
            self.channel.close()
            self.channel = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def _call_with_retry(self, method, request, metadata=None, max_retries=3, retry_delay=1):
        """
        Call gRPC method with retry logic
        
        Args:
            method: gRPC method to call
            request: Request object
            metadata: Call metadata
            max_retries: Maximum number of retries
            retry_delay: Delay between retries in seconds
        """
        metadata = metadata or []
        attempt = 0
        
        while attempt < max_retries:
            try:
                start_time = time.time()
                response = method(request, metadata=metadata, timeout=self.timeout)
                elapsed_time = time.time() - start_time
                
                # Log successful call
                logger.debug(
                    f"{self.service_name}.{method.__name__} call successful "
                    f"in {elapsed_time:.4f}s"
                )
                
                return response
            
            except grpc.RpcError as e:
                status_code = e.code()
                attempt += 1
                
                # Log the error
                logger.warning(
                    f"{self.service_name}.{method.__name__} failed with {status_code}: "
                    f"{e.details()} (Attempt {attempt}/{max_retries})"
                )
                
                # Determine if we should retry
                if attempt >= max_retries or not self._should_retry(status_code):
                    raise self._convert_exception(e)
                
                # Wait before retrying
                time.sleep(retry_delay * attempt)  # Exponential backoff
                
                # Reconnect if channel is in a bad state
                if status_code in [
                    grpc.StatusCode.UNAVAILABLE,
                    grpc.StatusCode.UNAUTHENTICATED
                ]:
                    self._connect()
    
    def _should_retry(self, status_code):
        """Determine if we should retry based on status code"""
        return status_code in [
            grpc.StatusCode.UNAVAILABLE,
            grpc.StatusCode.DEADLINE_EXCEEDED,
            grpc.StatusCode.RESOURCE_EXHAUSTED,
        ]
    
    def _convert_exception(self, grpc_error):
        """Convert gRPC error to custom exception"""
        status_code = grpc_error.code()
        
        if status_code == grpc.StatusCode.DEADLINE_EXCEEDED:
            return ServiceTimeoutError(
                f"{self.service_name} request timed out: {grpc_error.details()}"
            )
        elif status_code == grpc.StatusCode.UNAVAILABLE:
            return ServiceUnavailableError(
                f"{self.service_name} is unavailable: {grpc_error.details()}"
            )
        else:
            # Create appropriate exception based on status code
            from .exceptions import get_exception_for_status_code
            exception_class = get_exception_for_status_code(status_code)
            return exception_class(
                f"{self.service_name} error: {grpc_error.details()}"
            )
