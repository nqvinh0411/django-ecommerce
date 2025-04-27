from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import serializers, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response

from core.views.base import (
    BaseAPIView, BaseListView, BaseCreateView, BaseRetrieveView,
    BaseUpdateView, BaseDestroyView, BaseRetrieveUpdateDestroyView
)

User = get_user_model()


class TestModel:
    """Simple test model for testing views."""
    
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description
    
    def delete(self):
        """Mock delete method."""
        # In a real model, this would delete the object
        pass


class TestSerializer(serializers.Serializer):
    """Test serializer for our test model."""
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(required=False, allow_blank=True)
    
    def create(self, validated_data):
        return TestModel(
            id=99,  # Simulated ID generation
            name=validated_data['name'],
            description=validated_data.get('description', '')
        )
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        return instance


class TestBaseAPIView(TestCase):
    """Test cases for BaseAPIView."""
    
    class TestView(BaseAPIView):
        serializer_class = TestSerializer
        
        def get_object(self):
            return TestModel(id=1, name='Test', description='Test Description')
        
        def get_success_headers(self, data):
            return {'Custom-Header': 'Test'}
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = self.TestView.as_view()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
    
    def test_create_method(self):
        """Test the create method of BaseAPIView."""
        request = self.factory.post('/', {'name': 'New Test', 'description': 'New Description'})
        force_authenticate(request, user=self.user)
        
        # Add test method to view
        self.TestView.post = lambda self, request: self.create(request)
        view = self.TestView.as_view()
        
        response = view(request)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['status_code'], status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Tạo mới thành công')
        self.assertEqual(response.data['data']['name'], 'New Test')
        self.assertEqual(response.data['data']['description'], 'New Description')
        self.assertEqual(response['Custom-Header'], 'Test')
    
    def test_update_method(self):
        """Test the update method of BaseAPIView."""
        request = self.factory.put('/', {'name': 'Updated Test', 'description': 'Updated Description'})
        force_authenticate(request, user=self.user)
        
        # Add test method to view
        self.TestView.put = lambda self, request: self.update(request)
        view = self.TestView.as_view()
        
        response = view(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['status_code'], status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Cập nhật thành công')
        self.assertEqual(response.data['data']['name'], 'Updated Test')
        self.assertEqual(response.data['data']['description'], 'Updated Description')
    
    def test_destroy_method(self):
        """Test the destroy method of BaseAPIView."""
        request = self.factory.delete('/')
        force_authenticate(request, user=self.user)
        
        # Add test method to view
        self.TestView.delete = lambda self, request: self.destroy(request)
        view = self.TestView.as_view()
        
        response = view(request)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['status_code'], status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['message'], 'Xóa thành công')


# Mock QuerySet for testing list views
class MockQuerySet:
    def __init__(self, items):
        self.items = items
    
    def all(self):
        return self
    
    def filter(self, **kwargs):
        return self
    
    def __getitem__(self, key):
        if isinstance(key, slice):
            return self.items[key.start:key.stop]
        return self.items[key]
    
    def __len__(self):
        return len(self.items)
    
    def count(self):
        return len(self.items)


class TestBaseListView(TestCase):
    """Test cases for BaseListView."""
    
    class TestListView(BaseListView):
        serializer_class = TestSerializer
        
        def get_queryset(self):
            return MockQuerySet([
                TestModel(id=1, name='Test 1', description='Description 1'),
                TestModel(id=2, name='Test 2', description='Description 2'),
                TestModel(id=3, name='Test 3', description='Description 3'),
            ])
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = self.TestListView.as_view()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
    
    def test_list_view(self):
        """Test that list view returns a properly formatted response."""
        request = self.factory.get('/')
        force_authenticate(request, user=self.user)
        
        response = self.view(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['status_code'], status.HTTP_200_OK)
        
        # Check data
        self.assertEqual(len(response.data['data']), 3)
        self.assertEqual(response.data['data'][0]['name'], 'Test 1')
        self.assertEqual(response.data['data'][1]['name'], 'Test 2')
        self.assertEqual(response.data['data'][2]['name'], 'Test 3')


class TestBaseCreateView(TestCase):
    """Test cases for BaseCreateView."""
    
    class TestCreateView(BaseCreateView):
        serializer_class = TestSerializer
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = self.TestCreateView.as_view()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
    
    def test_create_view(self):
        """Test that create view returns a properly formatted response."""
        request = self.factory.post('/', {'name': 'New Item', 'description': 'New Description'})
        force_authenticate(request, user=self.user)
        
        response = self.view(request)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['status_code'], status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Tạo mới thành công')
        
        # Check data
        self.assertEqual(response.data['data']['name'], 'New Item')
        self.assertEqual(response.data['data']['description'], 'New Description')


class TestBaseRetrieveUpdateDestroyView(TestCase):
    """Test cases for BaseRetrieveUpdateDestroyView."""
    
    class TestRUDView(BaseRetrieveUpdateDestroyView):
        serializer_class = TestSerializer
        
        def get_object(self):
            return TestModel(id=1, name='Test', description='Test Description')
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = self.TestRUDView.as_view()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
    
    def test_retrieve_view(self):
        """Test that retrieve view returns a properly formatted response."""
        request = self.factory.get('/')
        force_authenticate(request, user=self.user)
        
        response = self.view(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['status_code'], status.HTTP_200_OK)
        
        # Check data
        self.assertEqual(response.data['data']['id'], 1)
        self.assertEqual(response.data['data']['name'], 'Test')
        self.assertEqual(response.data['data']['description'], 'Test Description')
    
    def test_update_view(self):
        """Test that update view returns a properly formatted response."""
        request = self.factory.put('/', {'name': 'Updated', 'description': 'Updated Description'})
        force_authenticate(request, user=self.user)
        
        response = self.view(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['status_code'], status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Cập nhật thành công')
        
        # Check data
        self.assertEqual(response.data['data']['name'], 'Updated')
        self.assertEqual(response.data['data']['description'], 'Updated Description')
    
    def test_partial_update_view(self):
        """Test that partial update view returns a properly formatted response."""
        request = self.factory.patch('/', {'name': 'Partially Updated'})
        force_authenticate(request, user=self.user)
        
        response = self.view(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['message'], 'Cập nhật thành công')
        
        # Check data - only name should be updated
        self.assertEqual(response.data['data']['name'], 'Partially Updated')
        self.assertEqual(response.data['data']['description'], 'Test Description')
    
    def test_destroy_view(self):
        """Test that destroy view returns a properly formatted response."""
        request = self.factory.delete('/')
        force_authenticate(request, user=self.user)
        
        response = self.view(request)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['status_code'], status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['message'], 'Xóa thành công')
