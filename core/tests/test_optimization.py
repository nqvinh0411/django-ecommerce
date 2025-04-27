import time
from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory
from django.db.models import QuerySet
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response

from core.optimization.mixins import (
    QueryOptimizationMixin, DeferUnusedFieldsMixin,
    SliceQuerySetMixin, CountOptimizedPaginationMixin
)
from core.optimization.utils import (
    get_related_fields, get_prefetch_fields, optimize_queryset,
    count_database_queries
)
from core.optimization.decorators import (
    select_related_fields, prefetch_related_fields,
    auto_optimize_queryset, cached_property_with_ttl
)

User = get_user_model()


# Mock models for testing
class MockModel:
    class _meta:
        def __init__(self):
            self.fields = []
            
        def get_fields(self):
            return self.fields


class MockField:
    def __init__(self, name, field_type, related_model=None):
        self.name = name
        self.field_type = field_type
        self.is_relation = field_type in ['ForeignKey', 'OneToOneField', 'ManyToManyField']
        self.one_to_many = field_type == 'ManyToOneRel'
        self.many_to_many = field_type == 'ManyToManyRel'
        
        if related_model:
            self.remote_field = type('MockRemoteField', (), {'model': related_model})


class MockQuerySet:
    def __init__(self, model=None, items=None):
        self.model = model or MockModel()
        self.items = items or []
        self.select_related_calls = []
        self.prefetch_related_calls = []
        self.defer_calls = []
        self.only_calls = []
        self.filter_calls = []
        self.filter_params = []
        self.db = MagicMock()
    
    def select_related(self, *fields):
        self.select_related_calls.extend(fields)
        return self
    
    def prefetch_related(self, *fields):
        self.prefetch_related_calls.extend(fields)
        return self
    
    def defer(self, *fields):
        self.defer_calls.extend(fields)
        return self
    
    def only(self, *fields):
        self.only_calls.extend(fields)
        return self
    
    def filter(self, **kwargs):
        self.filter_calls.append(kwargs)
        self.filter_params.append(kwargs)
        return self
    
    def all(self):
        return self
    
    def count(self):
        return len(self.items)
    
    def __getitem__(self, key):
        if isinstance(key, slice):
            return MockQuerySet(self.model, self.items[key.start:key.stop])
        return self.items[key]
    
    def __len__(self):
        return len(self.items)


class TestQueryOptimizationMixin(TestCase):
    """Test the QueryOptimizationMixin."""
    
    class TestView(QueryOptimizationMixin, APIView):
        select_related_fields = ['user']
        prefetch_related_fields = ['tags']
        
        def get_queryset(self):
            return MockQuerySet(MockModel())
    
    def setUp(self):
        self.view = self.TestView()
    
    def test_get_queryset_applies_optimizations(self):
        """Test that get_queryset applies select_related and prefetch_related."""
        with patch('core.optimization.mixins.get_related_fields', return_value=['category', 'brand']):
            with patch('core.optimization.mixins.get_prefetch_fields', return_value=['reviews']):
                queryset = self.view.get_queryset()
                
                # Should include both explicit and automatic fields
                self.assertIn('user', queryset.select_related_calls)
                self.assertIn('category', queryset.select_related_calls)
                self.assertIn('brand', queryset.select_related_calls)
                
                self.assertIn('tags', queryset.prefetch_related_calls)
                self.assertIn('reviews', queryset.prefetch_related_calls)
    
    def test_disable_automatic_optimization(self):
        """Test that automatic optimization can be disabled."""
        self.view.disable_automatic_optimization = True
        
        queryset = self.view.get_queryset()
        
        # Should only include explicit fields, not automatic ones
        self.assertIn('user', queryset.select_related_calls)
        self.assertIn('tags', queryset.prefetch_related_calls)
        
        # No automatic fields should be added
        self.assertEqual(len(queryset.select_related_calls), 1)
        self.assertEqual(len(queryset.prefetch_related_calls), 1)


class TestDeferUnusedFieldsMixin(TestCase):
    """Test the DeferUnusedFieldsMixin."""
    
    def test_fields_to_include(self):
        """Test that fields_to_include applies only()."""
        class TestView(DeferUnusedFieldsMixin, APIView):
            fields_to_include = ['id', 'name', 'price']
            
            def get_queryset(self):
                return MockQuerySet()
        
        view = TestView()
        queryset = view.get_queryset()
        
        self.assertEqual(queryset.only_calls, ['id', 'name', 'price'])
        self.assertEqual(queryset.defer_calls, [])  # Should not call defer()
    
    def test_fields_to_defer(self):
        """Test that fields_to_defer applies defer()."""
        class TestView(DeferUnusedFieldsMixin, APIView):
            fields_to_defer = ['description', 'meta_data']
            
            def get_queryset(self):
                return MockQuerySet()
        
        view = TestView()
        queryset = view.get_queryset()
        
        self.assertEqual(queryset.defer_calls, ['description', 'meta_data'])
        self.assertEqual(queryset.only_calls, [])  # Should not call only()
    
    def test_no_fields_specified(self):
        """Test that no optimization is applied if no fields are specified."""
        class TestView(DeferUnusedFieldsMixin, APIView):
            def get_queryset(self):
                return MockQuerySet()
        
        view = TestView()
        queryset = view.get_queryset()
        
        self.assertEqual(queryset.defer_calls, [])
        self.assertEqual(queryset.only_calls, [])


class TestUtilityFunctions(TestCase):
    """Test the utility functions."""
    
    def setUp(self):
        # Create mock models with relationships
        self.product_model = MockModel()
        self.category_model = MockModel()
        self.brand_model = MockModel()
        self.review_model = MockModel()
        
        # Add fields to product model
        self.product_model._meta.fields = [
            MockField('category', 'ForeignKey', self.category_model),
            MockField('brand', 'ForeignKey', self.brand_model),
            MockField('name', 'CharField'),
            MockField('price', 'DecimalField'),
            MockField('reviews', 'ManyToOneRel'),
        ]
        
        # Make get_fields return the fields
        self.product_model._meta.get_fields = lambda: self.product_model._meta.fields
    
    @patch('django.db.models.fields.related.ForeignKey', MagicMock())
    @patch('django.db.models.fields.related.OneToOneField', MagicMock())
    def test_get_related_fields(self):
        """Test get_related_fields returns correct fields."""
        with patch('core.optimization.utils.isinstance', return_value=True):
            fields = get_related_fields(self.product_model, max_depth=1)
            
            # Should include all ForeignKey and OneToOneField relationships
            self.assertEqual(len(fields), 2)
            self.assertIn('category', fields)
            self.assertIn('brand', fields)
    
    @patch('django.db.models.fields.related.ManyToManyField', MagicMock())
    @patch('django.db.models.fields.reverse_related.ManyToOneRel', MagicMock())
    @patch('django.db.models.fields.reverse_related.ManyToManyRel', MagicMock())
    def test_get_prefetch_fields(self):
        """Test get_prefetch_fields returns correct fields."""
        with patch('core.optimization.utils.isinstance', side_effect=lambda obj, types: obj.field_type in ['ManyToManyField', 'ManyToOneRel', 'ManyToManyRel']):
            # Mock get_accessor_name for reverse relations
            for field in self.product_model._meta.fields:
                if field.field_type == 'ManyToOneRel':
                    field.get_accessor_name = lambda: 'reviews'
                    field.related_name = 'reviews'
            
            fields = get_prefetch_fields(self.product_model)
            
            # Should include ManyToMany and reverse relations
            self.assertEqual(len(fields), 1)
            self.assertIn('reviews', fields)
    
    def test_optimize_queryset(self):
        """Test optimize_queryset applies all optimizations."""
        queryset = MockQuerySet()
        
        optimized = optimize_queryset(
            queryset,
            select_fields=['category', 'brand'],
            prefetch_fields=['reviews', 'tags'],
            defer_fields=['description']
        )
        
        self.assertEqual(optimized.select_related_calls, ['category', 'brand'])
        self.assertEqual(optimized.prefetch_related_calls, ['reviews', 'tags'])
        self.assertEqual(optimized.defer_calls, ['description'])
        
        # Test with only_fields instead of defer_fields
        queryset = MockQuerySet()
        
        optimized = optimize_queryset(
            queryset,
            select_fields=['category'],
            prefetch_fields=['reviews'],
            only_fields=['id', 'name', 'price']
        )
        
        self.assertEqual(optimized.only_calls, ['id', 'name', 'price'])
        self.assertEqual(optimized.defer_calls, [])  # Should not call defer()


class TestDecorators(TestCase):
    """Test the decorator functions."""
    
    def test_select_related_fields_decorator(self):
        """Test select_related_fields decorator."""
        @select_related_fields('user', 'category')
        def get_queryset():
            return MockQuerySet()
        
        queryset = get_queryset()
        
        self.assertEqual(queryset.select_related_calls, ['user', 'category'])
    
    def test_prefetch_related_fields_decorator(self):
        """Test prefetch_related_fields decorator."""
        @prefetch_related_fields('reviews', 'tags')
        def get_queryset():
            return MockQuerySet()
        
        queryset = get_queryset()
        
        self.assertEqual(queryset.prefetch_related_calls, ['reviews', 'tags'])
    
    def test_auto_optimize_queryset_decorator(self):
        """Test auto_optimize_queryset decorator."""
        with patch('core.optimization.decorators.get_related_fields', return_value=['category']):
            with patch('core.optimization.decorators.get_prefetch_fields', return_value=['reviews']):
                @auto_optimize_queryset()
                def get_queryset():
                    return MockQuerySet(MockModel())
                
                queryset = get_queryset()
                
                self.assertEqual(queryset.select_related_calls, ['category'])
                self.assertEqual(queryset.prefetch_related_calls, ['reviews'])
    
    def test_cached_property_with_ttl(self):
        """Test cached_property_with_ttl decorator."""
        class TestClass:
            call_count = 0
            
            @cached_property_with_ttl(ttl=1)  # 1 second TTL
            def expensive_calculation(self):
                self.call_count += 1
                return 42
        
        obj = TestClass()
        
        # First call should compute the value
        value1 = obj.expensive_calculation
        self.assertEqual(value1, 42)
        self.assertEqual(obj.call_count, 1)
        
        # Second call should use cached value
        value2 = obj.expensive_calculation
        self.assertEqual(value2, 42)
        self.assertEqual(obj.call_count, 1)  # Should not increase
        
        # Wait for TTL to expire
        time.sleep(1.1)
        
        # Call after TTL expired should recompute
        value3 = obj.expensive_calculation
        self.assertEqual(value3, 42)
        self.assertEqual(obj.call_count, 2)  # Should increase
