from django.test import TestCase, RequestFactory
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from rest_framework.views import APIView
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.exceptions import ValidationError, NotFound, AuthenticationFailed
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from core.exceptions.handlers import (
    custom_exception_handler, ServiceUnavailable, BadRequest, ResourceNotFound,
    handler400, handler403, handler404, handler500
)


class TestCustomExceptions(TestCase):
    """Test cases for custom exception classes."""
    
    def test_service_unavailable_exception(self):
        """Test ServiceUnavailable exception."""
        exc = ServiceUnavailable()
        self.assertEqual(exc.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(str(exc.detail), 'Dịch vụ tạm thời không khả dụng, vui lòng thử lại sau.')
        self.assertEqual(exc.default_code, 'service_unavailable')
        
        # Test custom message
        custom_message = "Hệ thống đang bảo trì"
        exc = ServiceUnavailable(custom_message)
        self.assertEqual(str(exc.detail), custom_message)
    
    def test_bad_request_exception(self):
        """Test BadRequest exception."""
        exc = BadRequest()
        self.assertEqual(exc.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(exc.detail), 'Yêu cầu không hợp lệ.')
        self.assertEqual(exc.default_code, 'bad_request')
        
        # Test custom message
        custom_message = "Dữ liệu không hợp lệ"
        exc = BadRequest(custom_message)
        self.assertEqual(str(exc.detail), custom_message)
    
    def test_resource_not_found_exception(self):
        """Test ResourceNotFound exception."""
        exc = ResourceNotFound()
        self.assertEqual(exc.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(str(exc.detail), 'Không tìm thấy tài nguyên yêu cầu.')
        self.assertEqual(exc.default_code, 'resource_not_found')
        
        # Test custom message
        custom_message = "Sản phẩm không tồn tại"
        exc = ResourceNotFound(custom_message)
        self.assertEqual(str(exc.detail), custom_message)


class TestExceptionHandler(TestCase):
    """Test cases for the custom exception handler."""
    
    class TestView(APIView):
        permission_classes = [IsAuthenticated]
        
        def get(self, request):
            raise NotFound("Resource not found")
        
        def post(self, request):
            raise ValidationError({
                'email': ['Email không hợp lệ'],
                'password': ['Mật khẩu không đủ mạnh']
            })
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = self.TestView.as_view()
    
    def test_handle_not_found_exception(self):
        """Test handling NotFound exception."""
        request = self.factory.get('/')
        exc = NotFound("Test not found")
        response = custom_exception_handler(exc, {'request': request})
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(response.data['status_code'], status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Test not found')
    
    def test_handle_validation_error(self):
        """Test handling ValidationError with field errors."""
        request = self.factory.post('/')
        validation_errors = {
            'email': ['Email không hợp lệ'],
            'password': ['Mật khẩu không đủ mạnh']
        }
        exc = ValidationError(validation_errors)
        response = custom_exception_handler(exc, {'request': request})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(response.data['status_code'], status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Invalid input.')
        self.assertEqual(response.data['errors'], validation_errors)
    
    def test_handle_authentication_error(self):
        """Test handling AuthenticationFailed exception."""
        request = self.factory.get('/')
        exc = AuthenticationFailed("Xác thực không thành công")
        response = custom_exception_handler(exc, {'request': request})
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(response.data['status_code'], status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Xác thực không thành công')
    
    def test_handle_object_does_not_exist(self):
        """Test that ObjectDoesNotExist is converted to ResourceNotFound."""
        request = self.factory.get('/')
        
        class CustomObjectDoesNotExist(ObjectDoesNotExist):
            pass
        
        exc = CustomObjectDoesNotExist("Object not found")
        response = custom_exception_handler(exc, {'request': request})
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(response.data['status_code'], status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Không tìm thấy tài nguyên yêu cầu.')


class TestHttpErrorHandlers(TestCase):
    """Test cases for HTTP error handlers."""
    
    def test_handler400(self):
        """Test handler400 returns properly formatted response."""
        request = RequestFactory().get('/')
        response = handler400(request)
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['status_code'], 400)
        self.assertEqual(data['message'], 'Yêu cầu không hợp lệ.')
    
    def test_handler403(self):
        """Test handler403 returns properly formatted response."""
        request = RequestFactory().get('/')
        response = handler403(request)
        
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['status_code'], 403)
        self.assertEqual(data['message'], 'Bạn không có quyền truy cập tài nguyên này.')
    
    def test_handler404(self):
        """Test handler404 returns properly formatted response."""
        request = RequestFactory().get('/')
        response = handler404(request)
        
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['status_code'], 404)
        self.assertEqual(data['message'], 'Không tìm thấy tài nguyên yêu cầu.')
    
    def test_handler500(self):
        """Test handler500 returns properly formatted response."""
        request = RequestFactory().get('/')
        response = handler500(request)
        
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['status_code'], 500)
        self.assertEqual(data['message'], 'Đã xảy ra lỗi server. Chúng tôi đang khắc phục sự cố.')
