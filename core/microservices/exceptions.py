"""
Custom exceptions for microservice communication
"""

import grpc


class MicroserviceError(Exception):
    """Base exception for all microservice errors"""
    def __init__(self, message, status_code=None, details=None):
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class ServiceUnavailableError(MicroserviceError):
    """Raised when a microservice is unavailable"""
    pass


class ServiceTimeoutError(MicroserviceError):
    """Raised when a microservice request times out"""
    pass


class AuthenticationError(MicroserviceError):
    """Raised when authentication fails"""
    pass


class AuthorizationError(MicroserviceError):
    """Raised when authorization fails"""
    pass


class ValidationError(MicroserviceError):
    """Raised when request validation fails"""
    pass


class ResourceNotFoundError(MicroserviceError):
    """Raised when a requested resource is not found"""
    pass


class ConflictError(MicroserviceError):
    """Raised when there's a conflict with current state"""
    pass


# Mapping from gRPC status codes to exception classes
_STATUS_CODE_TO_EXCEPTION = {
    grpc.StatusCode.CANCELLED: MicroserviceError,
    grpc.StatusCode.UNKNOWN: MicroserviceError,
    grpc.StatusCode.INVALID_ARGUMENT: ValidationError,
    grpc.StatusCode.DEADLINE_EXCEEDED: ServiceTimeoutError,
    grpc.StatusCode.NOT_FOUND: ResourceNotFoundError,
    grpc.StatusCode.ALREADY_EXISTS: ConflictError,
    grpc.StatusCode.PERMISSION_DENIED: AuthorizationError,
    grpc.StatusCode.RESOURCE_EXHAUSTED: ServiceUnavailableError,
    grpc.StatusCode.FAILED_PRECONDITION: ValidationError,
    grpc.StatusCode.ABORTED: ConflictError,
    grpc.StatusCode.OUT_OF_RANGE: ValidationError,
    grpc.StatusCode.UNIMPLEMENTED: MicroserviceError,
    grpc.StatusCode.INTERNAL: MicroserviceError,
    grpc.StatusCode.UNAVAILABLE: ServiceUnavailableError,
    grpc.StatusCode.DATA_LOSS: MicroserviceError,
    grpc.StatusCode.UNAUTHENTICATED: AuthenticationError,
}


def get_exception_for_status_code(status_code):
    """
    Get the appropriate exception class for a gRPC status code
    
    Args:
        status_code: gRPC status code
    
    Returns:
        Exception class
    """
    return _STATUS_CODE_TO_EXCEPTION.get(status_code, MicroserviceError)
