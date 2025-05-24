"""
gRPC client interceptors and middleware
"""

import logging
import time
import uuid
import grpc
from django.conf import settings

logger = logging.getLogger(__name__)


class AuthInterceptor(grpc.UnaryUnaryClientInterceptor, 
                     grpc.UnaryStreamClientInterceptor,
                     grpc.StreamUnaryClientInterceptor,
                     grpc.StreamStreamClientInterceptor):
    """
    Interceptor for adding authentication metadata to gRPC calls
    """
    
    def __init__(self, auth_token_provider):
        """
        Initialize with a callable that provides auth tokens
        
        Args:
            auth_token_provider: Callable that returns an auth token
        """
        self.auth_token_provider = auth_token_provider
    
    def _add_auth_metadata(self, metadata):
        """Add authentication token to metadata"""
        metadata = list(metadata) if metadata else []
        
        # Add auth token to metadata if not already present
        if not any(key.lower() == 'authorization' for key, _ in metadata):
            token = self.auth_token_provider()
            if token:
                metadata.append(('authorization', f'Bearer {token}'))
        
        return metadata
    
    def intercept_unary_unary(self, continuation, client_call_details, request):
        metadata = self._add_auth_metadata(client_call_details.metadata)
        new_details = _create_client_call_details(
            client_call_details, metadata=metadata
        )
        return continuation(new_details, request)
    
    def intercept_unary_stream(self, continuation, client_call_details, request):
        metadata = self._add_auth_metadata(client_call_details.metadata)
        new_details = _create_client_call_details(
            client_call_details, metadata=metadata
        )
        return continuation(new_details, request)
    
    def intercept_stream_unary(self, continuation, client_call_details, request_iterator):
        metadata = self._add_auth_metadata(client_call_details.metadata)
        new_details = _create_client_call_details(
            client_call_details, metadata=metadata
        )
        return continuation(new_details, request_iterator)
    
    def intercept_stream_stream(self, continuation, client_call_details, request_iterator):
        metadata = self._add_auth_metadata(client_call_details.metadata)
        new_details = _create_client_call_details(
            client_call_details, metadata=metadata
        )
        return continuation(new_details, request_iterator)


class MetricsInterceptor(grpc.UnaryUnaryClientInterceptor):
    """
    Interceptor for collecting metrics on gRPC calls
    """
    
    def __init__(self, service_name):
        """
        Initialize with service name for logging
        
        Args:
            service_name: Name of the service being called
        """
        self.service_name = service_name
    
    def intercept_unary_unary(self, continuation, client_call_details, request):
        start_time = time.time()
        
        # Generate a request ID for tracing
        request_id = str(uuid.uuid4())
        metadata = list(client_call_details.metadata or [])
        metadata.append(('x-request-id', request_id))
        
        # Create new client call details with the updated metadata
        new_details = _create_client_call_details(
            client_call_details, metadata=metadata
        )
        
        # Log the request
        method_name = client_call_details.method.decode('utf-8').split('/')[-1]
        logger.debug(f"Calling {self.service_name}.{method_name} [request_id={request_id}]")
        
        try:
            response = continuation(new_details, request)
            elapsed_time = time.time() - start_time
            
            # Log the successful response time
            logger.debug(
                f"{self.service_name}.{method_name} completed in {elapsed_time:.4f}s "
                f"[request_id={request_id}]"
            )
            
            return response
            
        except grpc.RpcError as e:
            elapsed_time = time.time() - start_time
            
            # Log the error with detailed information
            logger.error(
                f"{self.service_name}.{method_name} failed in {elapsed_time:.4f}s "
                f"with {e.code()}: {e.details()} [request_id={request_id}]"
            )
            
            raise


def _create_client_call_details(client_call_details, metadata=None):
    """Create a new ClientCallDetails with updated metadata"""
    if metadata is not None:
        return _ClientCallDetails(
            client_call_details.method,
            client_call_details.timeout,
            metadata,
            client_call_details.credentials,
            client_call_details.wait_for_ready,
            client_call_details.compression
        )
    return client_call_details


class _ClientCallDetails(grpc.ClientCallDetails):
    """Simple implementation of grpc.ClientCallDetails"""
    
    def __init__(self, method, timeout, metadata, credentials,
                 wait_for_ready, compression):
        self.method = method
        self.timeout = timeout
        self.metadata = metadata
        self.credentials = credentials
        self.wait_for_ready = wait_for_ready
        self.compression = compression
