from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from core.permissions.permissions import (
    IsOwnerOrAdmin, IsAdminOrReadOnly, IsSellerOrAdmin
)

User = get_user_model()


class TestIsOwnerOrAdmin(TestCase):
    """Test cases for IsOwnerOrAdmin permission."""
    
    class TestObject:
        def __init__(self, user):
            self.user = user
            self.owner = user  # For testing different owner_field
    
    class TestView(APIView):
        permission_classes = [IsOwnerOrAdmin]
    
    def setUp(self):
        self.factory = APIRequestFactory()
        
        # Create regular user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create another user
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpassword'
        )
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='testpassword',
            is_staff=True
        )
        
        # Create view instance
        self.view = self.TestView()
        self.view.request = self.factory.get('/')
    
    def test_user_is_owner(self):
        """Test permission when user is the owner."""
        # Set up request with regular user
        self.view.request.user = self.user
        
        # Create object owned by the same user
        obj = self.TestObject(self.user)
        
        # Set up the view with the object
        self.view.get_object = lambda: obj
        
        # Check permission
        permission = IsOwnerOrAdmin()
        self.assertTrue(permission.has_object_permission(self.view.request, self.view, obj))
    
    def test_user_is_not_owner(self):
        """Test permission when user is not the owner."""
        # Set up request with regular user
        self.view.request.user = self.user
        
        # Create object owned by another user
        obj = self.TestObject(self.other_user)
        
        # Set up the view with the object
        self.view.get_object = lambda: obj
        
        # Check permission
        permission = IsOwnerOrAdmin()
        self.assertFalse(permission.has_object_permission(self.view.request, self.view, obj))
    
    def test_user_is_admin(self):
        """Test permission when user is an admin."""
        # Set up request with admin user
        self.view.request.user = self.admin_user
        
        # Create object owned by another user
        obj = self.TestObject(self.other_user)
        
        # Set up the view with the object
        self.view.get_object = lambda: obj
        
        # Check permission
        permission = IsOwnerOrAdmin()
        self.assertTrue(permission.has_object_permission(self.view.request, self.view, obj))
    
    def test_custom_owner_field(self):
        """Test permission with custom owner field."""
        # Set up request with regular user
        self.view.request.user = self.user
        
        # Create object with different owner field name
        obj = self.TestObject(self.user)
        
        # Set up the view with the object
        self.view.get_object = lambda: obj
        
        # Check permission with custom owner_field
        permission = IsOwnerOrAdmin(owner_field='owner')
        self.assertTrue(permission.has_object_permission(self.view.request, self.view, obj))


class TestIsAdminOrReadOnly(TestCase):
    """Test cases for IsAdminOrReadOnly permission."""
    
    class TestView(APIView):
        permission_classes = [IsAdminOrReadOnly]
    
    def setUp(self):
        self.factory = APIRequestFactory()
        
        # Create regular user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='testpassword',
            is_staff=True
        )
        
        # Create anonymous user
        self.anon_user = AnonymousUser()
    
    def test_read_methods(self):
        """Test permission for read methods (GET, HEAD, OPTIONS)."""
        permission = IsAdminOrReadOnly()
        
        # Test with regular user and GET request
        request = self.factory.get('/')
        request.user = self.user
        view = self.TestView()
        self.assertTrue(permission.has_permission(request, view))
        
        # Test with anonymous user and GET request
        request = self.factory.get('/')
        request.user = self.anon_user
        view = self.TestView()
        self.assertTrue(permission.has_permission(request, view))
        
        # Test with OPTIONS request
        request = self.factory.options('/')
        request.user = self.anon_user
        view = self.TestView()
        self.assertTrue(permission.has_permission(request, view))
    
    def test_write_methods(self):
        """Test permission for write methods (POST, PUT, PATCH, DELETE)."""
        permission = IsAdminOrReadOnly()
        
        # Test with regular user and POST request
        request = self.factory.post('/')
        request.user = self.user
        view = self.TestView()
        self.assertFalse(permission.has_permission(request, view))
        
        # Test with admin user and POST request
        request = self.factory.post('/')
        request.user = self.admin_user
        view = self.TestView()
        self.assertTrue(permission.has_permission(request, view))
        
        # Test with anonymous user and DELETE request
        request = self.factory.delete('/')
        request.user = self.anon_user
        view = self.TestView()
        self.assertFalse(permission.has_permission(request, view))


class TestIsSellerOrAdmin(TestCase):
    """Test cases for IsSellerOrAdmin permission."""
    
    class TestView(APIView):
        permission_classes = [IsSellerOrAdmin]
    
    def setUp(self):
        self.factory = APIRequestFactory()
        
        # Create regular user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create seller user
        self.seller_user = User.objects.create_user(
            username='selleruser',
            email='seller@example.com',
            password='testpassword'
        )
        self.seller_user.is_seller = True
        self.seller_user.save()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='testpassword',
            is_staff=True
        )
        
        # Create anonymous user
        self.anon_user = AnonymousUser()
    
    def test_regular_user(self):
        """Test permission with a regular user."""
        permission = IsSellerOrAdmin()
        
        request = self.factory.get('/')
        request.user = self.user
        view = self.TestView()
        
        self.assertFalse(permission.has_permission(request, view))
    
    def test_seller_user(self):
        """Test permission with a seller user."""
        permission = IsSellerOrAdmin()
        
        request = self.factory.get('/')
        request.user = self.seller_user
        view = self.TestView()
        
        self.assertTrue(permission.has_permission(request, view))
    
    def test_admin_user(self):
        """Test permission with an admin user."""
        permission = IsSellerOrAdmin()
        
        request = self.factory.get('/')
        request.user = self.admin_user
        view = self.TestView()
        
        self.assertTrue(permission.has_permission(request, view))
    
    def test_anonymous_user(self):
        """Test permission with an anonymous user."""
        permission = IsSellerOrAdmin()
        
        request = self.factory.get('/')
        request.user = self.anon_user
        view = self.TestView()
        
        self.assertFalse(permission.has_permission(request, view))
