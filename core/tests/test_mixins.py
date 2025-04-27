from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from rest_framework import status, serializers
from rest_framework.response import Response

from core.mixins.views import (
    ApiResponseMixin, SerializerContextMixin,
    PermissionByActionMixin, SerializerByActionMixin
)


class TestApiResponseMixin(TestCase):
    """Test cases for ApiResponseMixin."""
    
    class TestView(ApiResponseMixin, APIView):
        def get(self, request):
            return self.success_response(
                data={'key': 'value'},
                message="Test message",
                status_code=status.HTTP_200_OK
            )
        
        def post(self, request):
            return self.error_response(
                message="Error message",
                errors={'field': ['Error detail']},
                status_code=status.HTTP_400_BAD_REQUEST
            )
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = self.TestView.as_view()
    
    def test_success_response(self):
        """Test that success_response returns correctly formatted response."""
        request = self.factory.get('/')
        response = self.view(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['status_code'], status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Test message')
        self.assertEqual(response.data['data'], {'key': 'value'})
    
    def test_error_response(self):
        """Test that error_response returns correctly formatted response."""
        request = self.factory.post('/')
        response = self.view(request)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(response.data['status_code'], status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Error message')
        self.assertEqual(response.data['errors'], {'field': ['Error detail']})


class TestSerializerContextMixin(TestCase):
    """Test cases for SerializerContextMixin."""
    
    class TestSerializer(serializers.Serializer):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.context_checked = False
            
        def to_representation(self, instance):
            # Verify context contains expected keys
            assert 'request' in self.context
            assert 'format' in self.context
            assert 'view' in self.context
            self.context_checked = True
            return {'data': 'value'}
    
    class TestView(SerializerContextMixin, APIView):
        def get_serializer(self):
            return self.TestSerializer(
                instance={'test': 'data'},
                context=self.get_serializer_context()
            )
        
        def get(self, request, format=None):
            serializer = self.get_serializer()
            data = serializer.to_representation(None)
            return Response(data)
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = self.TestView.as_view()
    
    def test_serializer_context(self):
        """Test that serializer context includes expected values."""
        request = self.factory.get('/')
        response = self.view(request)
        
        # If we got here without assertion errors, the test passed
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'data': 'value'})


class TestPermissionByActionMixin(TestCase):
    """Test cases for PermissionByActionMixin."""
    
    class AllowPermission:
        def has_permission(self, request, view):
            return True
    
    class DenyPermission:
        def has_permission(self, request, view):
            return False
    
    class TestViewSet(PermissionByActionMixin, APIView):
        permission_classes = [TestPermissionByActionMixin.DenyPermission]
        permission_classes_by_action = {
            'list': [TestPermissionByActionMixin.AllowPermission],
            'retrieve': [TestPermissionByActionMixin.DenyPermission]
        }
        
        def initial(self, request, *args, **kwargs):
            self.action = kwargs.get('action', None)
            return super().initial(request, *args, **kwargs)
    
    def setUp(self):
        self.view = self.TestViewSet()
    
    def test_get_permissions_by_action(self):
        """Test that the correct permissions are returned based on action."""
        # Test list action (should use AllowPermission)
        self.view.action = 'list'
        permissions = self.view.get_permissions()
        self.assertEqual(len(permissions), 1)
        self.assertIsInstance(permissions[0], self.AllowPermission)
        
        # Test retrieve action (should use DenyPermission)
        self.view.action = 'retrieve'
        permissions = self.view.get_permissions()
        self.assertEqual(len(permissions), 1)
        self.assertIsInstance(permissions[0], self.DenyPermission)
        
        # Test undefined action (should use default permission_classes)
        self.view.action = 'undefined_action'
        permissions = self.view.get_permissions()
        self.assertEqual(len(permissions), 1)
        self.assertIsInstance(permissions[0], self.DenyPermission)


class TestSerializerByActionMixin(TestCase):
    """Test cases for SerializerByActionMixin."""
    
    class TestSerializer1(serializers.Serializer):
        pass
    
    class TestSerializer2(serializers.Serializer):
        pass
    
    class TestViewSet(SerializerByActionMixin, APIView):
        serializer_class = TestSerializerByActionMixin.TestSerializer1
        serializer_class_by_action = {
            'list': TestSerializerByActionMixin.TestSerializer2,
        }
        
        def initial(self, request, *args, **kwargs):
            self.action = kwargs.get('action', None)
            return super().initial(request, *args, **kwargs)
    
    def setUp(self):
        self.view = self.TestViewSet()
    
    def test_get_serializer_class_by_action(self):
        """Test that the correct serializer class is returned based on action."""
        # Test list action (should use TestSerializer2)
        self.view.action = 'list'
        serializer_class = self.view.get_serializer_class()
        self.assertEqual(serializer_class, self.TestSerializer2)
        
        # Test undefined action (should use default serializer_class)
        self.view.action = 'undefined_action'
        serializer_class = self.view.get_serializer_class()
        self.assertEqual(serializer_class, self.TestSerializer1)
