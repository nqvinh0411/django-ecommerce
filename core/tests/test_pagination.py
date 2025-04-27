from django.test import TestCase
from django.http import HttpRequest
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

# Import the pagination classes to be tested
from core.pagination.standard import StandardResultsSetPagination, CursorPagination


class MockObject:
    """Mock object for testing pagination."""
    def __init__(self, id, name):
        self.id = id
        self.name = name


class MockQuerySet:
    """Mock queryset for testing pagination."""
    def __init__(self, items):
        self.items = items
    
    def __getitem__(self, key):
        if isinstance(key, slice):
            return self.items[key.start:key.stop]
        return self.items[key]
    
    def __len__(self):
        return len(self.items)
    
    def count(self):
        return len(self.items)
    
    def all(self):
        return self


class TestStandardResultsSetPagination(TestCase):
    """Test cases for StandardResultsSetPagination."""
    
    def setUp(self):
        self.pagination = StandardResultsSetPagination()
        self.factory = APIRequestFactory()
        
        # Create mock objects
        self.objects = [
            MockObject(id=i, name=f"Product {i}")
            for i in range(1, 30)  # Create 29 mock objects
        ]
        
        # Create mock queryset
        self.queryset = MockQuerySet(self.objects)
        
    def test_default_page_size(self):
        """Test that default page size is applied correctly."""
        request = self.factory.get('/')
        result = self.pagination.paginate_queryset(self.queryset, request)
        
        # Check that only the default page size (should be 20) items are returned
        self.assertEqual(len(result), 20)
        self.assertEqual(result[0].id, 1)
        self.assertEqual(result[19].id, 20)
    
    def test_custom_page_size(self):
        """Test that custom page_size parameter works."""
        request = self.factory.get('/?page_size=10')
        result = self.pagination.paginate_queryset(self.queryset, request)
        
        # Check that only 10 items are returned
        self.assertEqual(len(result), 10)
        self.assertEqual(result[0].id, 1)
        self.assertEqual(result[9].id, 10)
    
    def test_max_page_size(self):
        """Test that page_size cannot exceed max_page_size."""
        # Request a page size larger than the max (which should be 100)
        request = self.factory.get('/?page_size=200')
        result = self.pagination.paginate_queryset(self.queryset, request)
        
        # Should be capped at max_page_size (100)
        # But since we only have 29 items in total, we get all of them
        self.assertEqual(len(result), 29)
    
    def test_second_page(self):
        """Test pagination of second page."""
        request = self.factory.get('/?page=2&page_size=10')
        result = self.pagination.paginate_queryset(self.queryset, request)
        
        # Should return the second page (items 11-20)
        self.assertEqual(len(result), 10)
        self.assertEqual(result[0].id, 11)
        self.assertEqual(result[9].id, 20)
    
    def test_get_paginated_response(self):
        """Test that get_paginated_response returns correct structure."""
        request = self.factory.get('/?page=2&page_size=10')
        self.pagination.paginate_queryset(self.queryset, request)
        
        response = self.pagination.get_paginated_response([
            {'id': obj.id, 'name': obj.name}
            for obj in self.objects[10:20]  # Simulating serialized data for page 2
        ])
        
        # Check response structure
        self.assertIsInstance(response, Response)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)
        
        # Check specific values
        self.assertEqual(response.data['count'], 29)
        self.assertIsNotNone(response.data['next'])  # Should have a next page
        self.assertIsNotNone(response.data['previous'])  # Should have a previous page
        self.assertEqual(len(response.data['results']), 10)
        
        # Check first and last items
        self.assertEqual(response.data['results'][0]['id'], 11)
        self.assertEqual(response.data['results'][9]['id'], 20)


class TestCursorPagination(TestCase):
    """Test cases for CursorPagination."""
    
    def setUp(self):
        self.pagination = CursorPagination()
        self.factory = APIRequestFactory()
        
        # Create mock objects with an ordering field (created_at)
        # For cursor pagination, objects must have a clear ordering
        self.objects = []
        for i in range(1, 30):
            obj = MockObject(id=i, name=f"Product {i}")
            obj.created_at = i  # Simple ordering field
            self.objects.append(obj)
        
        # Create mock queryset
        self.queryset = MockQuerySet(self.objects)
        
        # Add support for cursor pagination to the mock queryset
        def filter_func(**kwargs):
            # Simple filter implementation for cursor pagination
            if 'created_at__gt' in kwargs:
                return MockQuerySet([obj for obj in self.objects if obj.created_at > kwargs['created_at__gt']])
            if 'created_at__lt' in kwargs:
                return MockQuerySet([obj for obj in self.objects if obj.created_at < kwargs['created_at__lt']])
            return self.queryset
            
        self.queryset.filter = filter_func
        
        # Add order_by method
        def order_by(*args):
            # Simple order_by implementation
            reverse = False
            field = args[0]
            if field.startswith('-'):
                reverse = True
                field = field[1:]
            
            # Sort the items
            items = sorted(self.objects, key=lambda obj: getattr(obj, field), reverse=reverse)
            return MockQuerySet(items)
            
        self.queryset.order_by = order_by
    
    def test_default_page_size(self):
        """Test that default page size is applied correctly."""
        request = self.factory.get('/')
        result = self.pagination.paginate_queryset(self.queryset, request)
        
        # Check that only the default page size items are returned
        self.assertEqual(len(result), self.pagination.page_size)
    
    def test_next_page(self):
        """Test navigation to the next page using cursor."""
        # Get the first page
        request = self.factory.get('/')
        self.pagination.paginate_queryset(self.queryset, request)
        response_data = self.pagination.get_paginated_response([]).data
        
        # Get the cursor for the next page
        next_url = response_data['next']
        next_request = self.factory.get(next_url.split('?')[1])
        
        # Get the second page
        result = self.pagination.paginate_queryset(self.queryset, next_request)
        
        # Check that the second page starts after the first page
        self.assertGreater(result[0].id, self.pagination.page_size)
    
    def test_get_paginated_response_structure(self):
        """Test that get_paginated_response returns correct structure for cursor pagination."""
        request = self.factory.get('/')
        self.pagination.paginate_queryset(self.queryset, request)
        
        response = self.pagination.get_paginated_response([
            {'id': obj.id, 'name': obj.name}
            for obj in self.objects[:self.pagination.page_size]
        ])
        
        # Check response structure for cursor pagination
        self.assertIsInstance(response, Response)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)
        
        # For the first page, previous should be None
        self.assertIsNone(response.data['previous'])
        # But we should have a next page
        self.assertIsNotNone(response.data['next'])
        
        # Check results
        self.assertEqual(len(response.data['results']), self.pagination.page_size)
