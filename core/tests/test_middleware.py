from django.test import TestCase, RequestFactory
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.test import APIRequestFactory
from rest_framework import status

from core.middleware.response import StandardizedResponseMiddleware


class TestStandardizedResponseMiddleware(TestCase):
    """Test cases for StandardizedResponseMiddleware."""
    
    def setUp(self):
        self.middleware = StandardizedResponseMiddleware(get_response=lambda r: None)
        self.factory = RequestFactory()
        self.api_factory = APIRequestFactory()
    
    def test_process_non_api_response(self):
        """Test that non-API responses are not modified."""
        request = self.factory.get('/non-api-path')
        response = HttpResponse('Test response', content_type='text/plain')
        
        processed_response = self.middleware.process_response(request, response)
        
        # Verify the response is unchanged
        self.assertEqual(processed_response, response)
        self.assertEqual(processed_response.content, b'Test response')
    
    def test_process_non_drf_response(self):
        """Test that non-DRF responses are not modified."""
        request = self.factory.get('/api/test')
        response = HttpResponse('Test response', content_type='text/plain')
        
        processed_response = self.middleware.process_response(request, response)
        
        # Verify the response is unchanged
        self.assertEqual(processed_response, response)
        self.assertEqual(processed_response.content, b'Test response')
    
    def test_process_already_formatted_response(self):
        """Test that responses with 'status' field are not modified."""
        request = self.factory.get('/api/test')
        response = Response({
            'status': 'custom',
            'data': {'test': 'value'}
        })
        
        processed_response = self.middleware.process_response(request, response)
        
        # Verify the response is unchanged
        self.assertEqual(processed_response, response)
        self.assertEqual(processed_response.data['status'], 'custom')
    
    def test_process_successful_response(self):
        """Test that successful responses are correctly formatted."""
        request = self.factory.get('/api/test')
        response = Response({'test': 'value'}, status=status.HTTP_200_OK)
        
        processed_response = self.middleware.process_response(request, response)
        
        # Verify the response is correctly formatted
        self.assertEqual(processed_response.status_code, status.HTTP_200_OK)
        self.assertEqual(processed_response.data['status'], 'success')
        self.assertEqual(processed_response.data['status_code'], status.HTTP_200_OK)
        self.assertEqual(processed_response.data['data'], {'test': 'value'})
    
    def test_process_paginated_response(self):
        """Test that paginated responses are correctly formatted."""
        request = self.factory.get('/api/test')
        response = Response({
            'count': 10,
            'next': 'http://testserver/api/test?page=2',
            'previous': None,
            'results': [{'id': 1, 'name': 'Test'}]
        })
        
        processed_response = self.middleware.process_response(request, response)
        
        # Verify the response has status fields but maintains pagination structure
        self.assertEqual(processed_response.data['status'], 'success')
        self.assertEqual(processed_response.data['status_code'], status.HTTP_200_OK)
        self.assertEqual(processed_response.data['count'], 10)
        self.assertEqual(processed_response.data['next'], 'http://testserver/api/test?page=2')
        self.assertIsNone(processed_response.data['previous'])
        self.assertEqual(processed_response.data['results'], [{'id': 1, 'name': 'Test'}])
    
    def test_process_error_response(self):
        """Test that error responses are not modified."""
        request = self.factory.get('/api/test')
        response = Response(
            {'detail': 'Not found'},
            status=status.HTTP_404_NOT_FOUND
        )
        
        # The middleware should not modify error responses (this is handled by exception handlers)
        processed_response = self.middleware.process_response(request, response)
        self.assertEqual(processed_response, response)
        self.assertEqual(processed_response.data, {'detail': 'Not found'})
