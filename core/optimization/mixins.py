"""
Database optimization mixins for Django views.

This module provides mixins that can be used to optimize database queries in Django views,
particularly for improving performance in list views and detail views by automatically applying
select_related and prefetch_related based on model relationships.
"""
from django.db import models
from django.db.models.fields.related import ForeignKey, OneToOneField, ManyToManyField
from django.db.models.fields.reverse_related import ManyToOneRel, OneToOneRel, ManyToManyRel

from .utils import get_related_fields, get_prefetch_fields


class QueryOptimizationMixin:
    """
    Mixin that automatically optimizes querysets for views by applying select_related and
    prefetch_related based on model relationships.
    
    This mixin analyzes the model's relationships and automatically applies the appropriate
    optimization techniques to reduce the number of database queries.
    
    Attributes:
        select_related_fields (list): Additional fields to explicitly include in select_related.
        prefetch_related_fields (list): Additional fields to explicitly include in prefetch_related.
        disable_automatic_optimization (bool): Set to True to disable automatic optimization.
        max_select_related_depth (int): Maximum depth for automatic select_related detection.
    """
    
    select_related_fields = []
    prefetch_related_fields = []
    disable_automatic_optimization = False
    max_select_related_depth = 2
    
    def get_queryset(self):
        """
        Override the default get_queryset method to optimize database queries
        by applying select_related and prefetch_related.
        
        Returns:
            QuerySet: An optimized queryset with select_related and prefetch_related applied.
        """
        queryset = super().get_queryset()
        
        # If optimization is explicitly disabled, return the original queryset
        if self.disable_automatic_optimization:
            return queryset
        
        model = queryset.model
        
        # Apply automatic select_related for ForeignKey and OneToOneField relationships
        if not hasattr(self, '_select_related_fields_cache'):
            self._select_related_fields_cache = self.select_related_fields.copy()
            
            if not self.disable_automatic_optimization:
                auto_select_fields = get_related_fields(
                    model, 
                    max_depth=self.max_select_related_depth
                )
                self._select_related_fields_cache.extend(auto_select_fields)
        
        # Apply automatic prefetch_related for ManyToManyField and reverse relationships
        if not hasattr(self, '_prefetch_related_fields_cache'):
            self._prefetch_related_fields_cache = self.prefetch_related_fields.copy()
            
            if not self.disable_automatic_optimization:
                auto_prefetch_fields = get_prefetch_fields(model)
                self._prefetch_related_fields_cache.extend(auto_prefetch_fields)
        
        # Apply the optimizations
        if self._select_related_fields_cache:
            queryset = queryset.select_related(*self._select_related_fields_cache)
        
        if self._prefetch_related_fields_cache:
            queryset = queryset.prefetch_related(*self._prefetch_related_fields_cache)
        
        return queryset


class SliceQuerySetMixin:
    """
    Mixin that slices querysets based on pagination settings to avoid unnecessary queries.
    
    This is useful for improving performance when a queryset would potentially return
    a large number of results, but only a small subset is needed for the current page.
    
    Note: This mixin should be applied to views that use pagination.
    """
    
    def get_queryset(self):
        """
        Override the default get_queryset method to slice the queryset based on
        pagination settings to avoid fetching unneeded data.
        
        Returns:
            QuerySet: A sliced queryset based on pagination settings.
        """
        queryset = super().get_queryset()
        
        # Apply slicing based on pagination if available
        if hasattr(self, 'paginator') and hasattr(self, 'page_size'):
            # If we're on a specific page, we can optimize further
            page_number = self.request.query_params.get(self.page_kwarg, 1)
            try:
                page_number = int(page_number)
            except (TypeError, ValueError):
                page_number = 1
                
            # Calculate the slice bounds based on the page number and page size
            start = (page_number - 1) * self.paginator.page_size
            end = start + self.paginator.page_size
            
            # Add a small buffer to account for potential filtered items
            end += 5
            
            # Apply the slice to the queryset
            queryset = queryset[start:end]
        
        return queryset


class DeferUnusedFieldsMixin:
    """
    Mixin that defers loading of fields that are not used in the view.
    
    This can significantly improve performance for models with large text fields or 
    many columns when only a subset of fields are needed for display.
    
    Attributes:
        fields_to_include (list): Fields to explicitly include (others will be deferred).
        fields_to_defer (list): Fields to explicitly defer (others will be included).
    """
    
    fields_to_include = None  # If set, only these fields will be loaded
    fields_to_defer = None    # If set, these fields will be deferred
    
    def get_queryset(self):
        """
        Override the default get_queryset method to defer loading of unused fields.
        
        Returns:
            QuerySet: A queryset with defer() or only() applied as appropriate.
        """
        queryset = super().get_queryset()
        
        if self.fields_to_include:
            # Use only() when we have a specific set of fields to include
            queryset = queryset.only(*self.fields_to_include)
        elif self.fields_to_defer:
            # Use defer() when we have specific fields to exclude
            queryset = queryset.defer(*self.fields_to_defer)
            
        return queryset


class CountOptimizedPaginationMixin:
    """
    Mixin that optimizes count queries for pagination.
    
    Django's pagination performs a COUNT(*) query which can be expensive on large tables.
    This mixin provides an optimized counting approach for pagination, using an estimate
    when possible and falling back to exact count only when necessary.
    """
    
    use_estimated_count = True  # Set to False to always use exact count
    
    def paginate_queryset(self, queryset, page_size):
        """
        Override the paginate_queryset method to use an optimized count query.
        
        Args:
            queryset: The queryset to paginate.
            page_size: Number of items per page.
            
        Returns:
            tuple: (paginated queryset, page, paginator)
        """
        if hasattr(self, 'paginator') and self.use_estimated_count:
            # Try to get the paginator to use our optimized count method
            if hasattr(self.paginator, 'count') and callable(self.paginator.count):
                original_count = self.paginator.count
                
                def optimized_count(queryset):
                    try:
                        # For PostgreSQL, we can use an estimated count
                        if 'postgresql' in queryset.db.settings_dict['ENGINE']:
                            with queryset.db.connection.cursor() as cursor:
                                cursor.execute(
                                    "SELECT reltuples::bigint FROM pg_class WHERE relname = %s",
                                    [queryset.model._meta.db_table]
                                )
                                row = cursor.fetchone()
                                if row and row[0] > 0:
                                    return row[0]
                    except Exception:
                        # Fall back to exact count on any error
                        pass
                        
                    # Fall back to original count method
                    return original_count(queryset)
                
                # Replace the count method with our optimized version
                self.paginator.count = optimized_count
                
        # Call the original paginate_queryset method
        return super().paginate_queryset(queryset, page_size)
