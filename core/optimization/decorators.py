"""
Decorators for database query optimization.

This module provides decorators that can be applied to views, viewsets, or specific methods
to optimize database queries and improve performance.
"""
import functools
from django.db import models, connection
from django.db.models import QuerySet
from django.conf import settings

from .utils import get_related_fields, get_prefetch_fields, optimize_queryset


def select_related_fields(*fields):
    """
    Decorator that applies select_related to a queryset returned by the decorated method.
    
    This is useful for view methods like get_queryset or specific action methods in ViewSets.
    
    Args:
        *fields: Field names to pass to select_related().
        
    Returns:
        function: Decorated function that applies select_related to the queryset.
        
    Example:
        @select_related_fields('user', 'category')
        def get_queryset(self):
            return super().get_queryset()
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if isinstance(result, QuerySet):
                return result.select_related(*fields)
            return result
        return wrapper
    return decorator


def prefetch_related_fields(*fields):
    """
    Decorator that applies prefetch_related to a queryset returned by the decorated method.
    
    This is useful for view methods like get_queryset or specific action methods in ViewSets.
    
    Args:
        *fields: Field names to pass to prefetch_related().
        
    Returns:
        function: Decorated function that applies prefetch_related to the queryset.
        
    Example:
        @prefetch_related_fields('tags', 'reviews')
        def get_queryset(self):
            return super().get_queryset()
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if isinstance(result, QuerySet):
                return result.prefetch_related(*fields)
            return result
        return wrapper
    return decorator


def defer_fields(*fields):
    """
    Decorator that applies defer to a queryset returned by the decorated method.
    
    This is useful for deferring the loading of large text fields or other fields
    that are not needed for the main functionality.
    
    Args:
        *fields: Field names to pass to defer().
        
    Returns:
        function: Decorated function that applies defer to the queryset.
        
    Example:
        @defer_fields('long_description', 'html_content')
        def get_queryset(self):
            return super().get_queryset()
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if isinstance(result, QuerySet):
                return result.defer(*fields)
            return result
        return wrapper
    return decorator


def only_fields(*fields):
    """
    Decorator that applies only to a queryset returned by the decorated method.
    
    This is useful for specifying the exact fields that should be loaded, which can
    significantly reduce the query size for models with many fields.
    
    Args:
        *fields: Field names to pass to only().
        
    Returns:
        function: Decorated function that applies only to the queryset.
        
    Example:
        @only_fields('id', 'name', 'slug', 'price')
        def get_queryset(self):
            return super().get_queryset()
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if isinstance(result, QuerySet):
                return result.only(*fields)
            return result
        return wrapper
    return decorator


def auto_optimize_queryset(max_select_depth=2, max_prefetch_depth=1):
    """
    Decorator that automatically applies select_related and prefetch_related based on model relationships.
    
    This decorator analyzes the model's relationships and applies the appropriate optimizations
    to reduce the number of database queries.
    
    Args:
        max_select_depth (int): Maximum depth for automatic select_related detection.
        max_prefetch_depth (int): Maximum depth for automatic prefetch_related detection.
        
    Returns:
        function: Decorated function that automatically optimizes the queryset.
        
    Example:
        @auto_optimize_queryset(max_select_depth=2)
        def get_queryset(self):
            return super().get_queryset()
    """
    def decorator(func):
        # Cache for optimization fields to avoid recomputing for each call
        optimization_cache = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            if not isinstance(result, QuerySet):
                return result
                
            model = result.model
            cache_key = model.__name__
            
            # Use cached optimization fields if available
            if cache_key in optimization_cache:
                select_fields, prefetch_fields = optimization_cache[cache_key]
            else:
                # Auto-detect fields for optimization
                select_fields = get_related_fields(model, max_depth=max_select_depth)
                prefetch_fields = get_prefetch_fields(model, max_depth=max_prefetch_depth)
                
                # Cache the results
                optimization_cache[cache_key] = (select_fields, prefetch_fields)
            
            # Apply optimizations
            if select_fields:
                result = result.select_related(*select_fields)
            if prefetch_fields:
                result = result.prefetch_related(*prefetch_fields)
                
            return result
            
        return wrapper
    return decorator


def log_slow_queries(threshold_ms=500):
    """
    Decorator that logs slow database queries executed during a function call.
    
    This is useful for identifying performance bottlenecks in views or other database-heavy
    functions. It will log any query that takes longer than the threshold.
    
    Args:
        threshold_ms (int): Time threshold in milliseconds. Queries taking longer will be logged.
        
    Returns:
        function: Decorated function that logs slow queries.
        
    Example:
        @log_slow_queries(threshold_ms=200)
        def my_expensive_view(request):
            # View code here
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Only enable in debug mode or if explicitly configured
            if not getattr(settings, 'QUERY_LOGGING_ENABLED', settings.DEBUG):
                return func(*args, **kwargs)
                
            # Chỉ ghi lại truy vấn khi DEBUG=True
            if settings.DEBUG:
                # Lưu số lượng truy vấn ban đầu
                initial_queries = len(connection.queries)
                
                # Đảm bảo query logging được bật
                connection.force_debug_cursor = True
                
                # Gọi hàm gốc
                result = func(*args, **kwargs)
                
                # Kiểm tra các truy vấn chậm
                for i in range(initial_queries, len(connection.queries)):
                    query = connection.queries[i]
                    if float(query.get('time', 0)) * 1000 > threshold_ms:
                        import logging
                        logger = logging.getLogger('django.db.backends')
                        logger.warning(
                            f"Slow query in {func.__name__}: {query.get('time')}s - {query.get('sql')}"
                        )
                
                return result
            else:
                # Nếu không ở chế độ debug, chỉ thực thi hàm mà không ghi log
                return func(*args, **kwargs)
                
        return wrapper
    return decorator


def cached_property_with_ttl(ttl=None):
    """
    Decorator that converts a method into a cached property with time-to-live.
    
    Similar to Django's cached_property, but with an optional TTL to invalidate the cache.
    This is useful for properties that are expensive to compute but may change over time.
    
    Args:
        ttl (int, optional): Time-to-live in seconds. If None, the cache never expires.
        
    Returns:
        property: Cached property that will be recomputed after TTL expires.
        
    Example:
        class Product(models.Model):
            @cached_property_with_ttl(ttl=3600)  # Cache for 1 hour
            def calculated_rating(self):
                # Expensive calculation
                return self.reviews.aggregate(Avg('rating'))['rating__avg']
    """
    def decorator(func):
        import time
        
        @property
        @functools.wraps(func)
        def wrapper(self):
            cache_name = f"_cached_{func.__name__}"
            timestamp_name = f"_cached_{func.__name__}_timestamp"
            
            # Check if cache exists and is still valid
            if hasattr(self, cache_name) and (
                ttl is None or 
                (hasattr(self, timestamp_name) and time.time() - getattr(self, timestamp_name) < ttl)
            ):
                return getattr(self, cache_name)
                
            # Compute and cache the value
            value = func(self)
            setattr(self, cache_name, value)
            
            # Set timestamp if TTL is used
            if ttl is not None:
                setattr(self, timestamp_name, time.time())
                
            return value
            
        return wrapper
    return decorator
