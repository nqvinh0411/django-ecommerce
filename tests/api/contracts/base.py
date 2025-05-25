"""
Base Contract Test Classes.

Module này cung cấp các lớp cơ sở cho việc kiểm tra hợp đồng (contract testing)
giữa các API và tài liệu API đã định nghĩa, đảm bảo tính nhất quán trong
toàn bộ hệ thống.
"""

from rest_framework.test import APITestCase
from rest_framework import status


class BaseContractTestCase(APITestCase):
    """
    Lớp cơ sở cho tất cả các test kiểm tra hợp đồng API.
    
    Lớp này cung cấp các phương thức và utilities chung để kiểm tra xem
    API responses có tuân thủ định dạng đã chuẩn hóa hay không.
    """
    
    def assert_success_response_format(self, response, status_code=status.HTTP_200_OK):
        """
        Kiểm tra xem response thành công có tuân thủ định dạng chuẩn không.
        
        Args:
            response: Response object từ API
            status_code (int, optional): HTTP status code mong đợi. Mặc định: 200.
            
        Raises:
            AssertionError: Nếu response không tuân thủ định dạng chuẩn
        """
        self.assertEqual(response.status_code, status_code)
        self.assertIn('status', response.data)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('status_code', response.data)
        self.assertEqual(response.data['status_code'], status_code)
        
        # Kiểm tra data field cho responses không phải 204 No Content
        if status_code != status.HTTP_204_NO_CONTENT:
            self.assertIn('data', response.data)
    
    def assert_error_response_format(self, response, status_code=status.HTTP_400_BAD_REQUEST):
        """
        Kiểm tra xem response lỗi có tuân thủ định dạng chuẩn không.
        
        Args:
            response: Response object từ API
            status_code (int, optional): HTTP status code mong đợi. Mặc định: 400.
            
        Raises:
            AssertionError: Nếu response không tuân thủ định dạng chuẩn
        """
        self.assertEqual(response.status_code, status_code)
        self.assertIn('status', response.data)
        self.assertEqual(response.data['status'], 'error')
        self.assertIn('status_code', response.data)
        self.assertEqual(response.data['status_code'], status_code)
        self.assertIn('message', response.data)
    
    def assert_paginated_response_format(self, response):
        """
        Kiểm tra xem response phân trang có tuân thủ định dạng chuẩn không.
        
        Args:
            response: Response object từ API
            
        Raises:
            AssertionError: Nếu response không tuân thủ định dạng phân trang chuẩn
        """
        self.assert_success_response_format(response)
        self.assertIn('data', response.data)
        self.assertIn('pagination', response.data)
        
        pagination = response.data['pagination']
        self.assertIn('count', pagination)
        self.assertIn('page_size', pagination)
        self.assertIn('current_page', pagination)
        self.assertIn('total_pages', pagination)
        self.assertIn('next', pagination)
        self.assertIn('previous', pagination)
    
    def assert_response_headers(self, response, expected_headers=None):
        """
        Kiểm tra xem response headers có chứa các headers mong đợi không.
        
        Args:
            response: Response object từ API
            expected_headers (dict, optional): Headers mong đợi. Mặc định: None.
            
        Raises:
            AssertionError: Nếu response không chứa headers mong đợi
        """
        if expected_headers:
            for header, value in expected_headers.items():
                self.assertIn(header, response)
                self.assertEqual(response[header], value)
    
    def assert_authentication_error(self, response):
        """
        Kiểm tra xem response lỗi xác thực có tuân thủ định dạng chuẩn không.
        
        Args:
            response: Response object từ API
            
        Raises:
            AssertionError: Nếu response không tuân thủ định dạng lỗi xác thực chuẩn
        """
        self.assert_error_response_format(response, status.HTTP_401_UNAUTHORIZED)
    
    def assert_permission_error(self, response):
        """
        Kiểm tra xem response lỗi phân quyền có tuân thủ định dạng chuẩn không.
        
        Args:
            response: Response object từ API
            
        Raises:
            AssertionError: Nếu response không tuân thủ định dạng lỗi phân quyền chuẩn
        """
        self.assert_error_response_format(response, status.HTTP_403_FORBIDDEN)
    
    def assert_validation_error(self, response):
        """
        Kiểm tra xem response lỗi validation có tuân thủ định dạng chuẩn không.
        
        Args:
            response: Response object từ API
            
        Raises:
            AssertionError: Nếu response không tuân thủ định dạng lỗi validation chuẩn
        """
        self.assert_error_response_format(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', response.data)
    
    def assert_not_found_error(self, response):
        """
        Kiểm tra xem response lỗi not found có tuân thủ định dạng chuẩn không.
        
        Args:
            response: Response object từ API
            
        Raises:
            AssertionError: Nếu response không tuân thủ định dạng lỗi not found chuẩn
        """
        self.assert_error_response_format(response, status.HTTP_404_NOT_FOUND)
