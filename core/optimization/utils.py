"""
Utility functions for database query optimization.

This module provides functions to help optimize database queries in Django applications,
particularly for handling select_related and prefetch_related operations automatically.
"""
from django.db import models
from django.db.models.fields.related import ForeignKey, OneToOneField, ManyToManyField
from django.db.models.fields.reverse_related import ManyToOneRel, OneToOneRel, ManyToManyRel


def get_related_fields(model, max_depth=2, current_depth=0, prefix='', processed_models=None):
    """
    Automatically detect fields suitable for select_related based on model relationships.
    
    This function analyzes a model's fields and returns a list of relationship paths
    that are suitable for use with select_related().
    
    Args:
        model: The Django model class to analyze.
        max_depth (int): Maximum depth to traverse relationships.
        current_depth (int): Current recursion depth (used internally).
        prefix (str): Current path prefix (used internally).
        processed_models (set): Set of models already processed to avoid recursion loops.
        
    Returns:
        list: A list of field paths suitable for select_related().
    """
    if processed_models is None:
        processed_models = set()
        
    # If we've reached maximum depth or already processed this model, stop recursion
    if current_depth >= max_depth or model in processed_models:
        return []
        
    processed_models.add(model)
    select_related_fields = []
    
    # Get all fields from the model
    for field in model._meta.get_fields():
        # Check if field is a ForeignKey or OneToOneField
        if isinstance(field, (ForeignKey, OneToOneField)):
            field_name = field.name
            if prefix:
                field_path = f"{prefix}__{field_name}"
            else:
                field_path = field_name
                
            select_related_fields.append(field_path)
            
            # Recursively get fields from related model
            related_model = field.remote_field.model
            if related_model != model:  # Avoid self-referential loops
                nested_fields = get_related_fields(
                    related_model, 
                    max_depth=max_depth,
                    current_depth=current_depth + 1,
                    prefix=field_path,
                    processed_models=processed_models.copy()
                )
                select_related_fields.extend(nested_fields)
    
    return select_related_fields


def get_prefetch_fields(model, max_depth=1, current_depth=0, prefix='', processed_models=None):
    """
    Automatically detect fields suitable for prefetch_related based on model relationships.
    
    This function analyzes a model's fields and returns a list of relationship paths
    that are suitable for use with prefetch_related().
    
    Args:
        model: The Django model class to analyze.
        max_depth (int): Maximum depth to traverse relationships.
        current_depth (int): Current recursion depth (used internally).
        prefix (str): Current path prefix (used internally).
        processed_models (set): Set of models already processed to avoid recursion loops.
        
    Returns:
        list: A list of field paths suitable for prefetch_related().
    """
    if processed_models is None:
        processed_models = set()
        
    # If we've reached maximum depth or already processed this model, stop recursion
    if current_depth >= max_depth or model in processed_models:
        return []
        
    processed_models.add(model)
    prefetch_fields = []
    
    # Get all fields from the model
    for field in model._meta.get_fields():
        # Handle ManyToMany fields
        if isinstance(field, ManyToManyField):
            field_name = field.name
            if prefix:
                field_path = f"{prefix}__{field_name}"
            else:
                field_path = field_name
                
            prefetch_fields.append(field_path)
            
        # Handle reverse relations
        elif isinstance(field, (ManyToOneRel, ManyToManyRel)):
            # Skip auto-created reverse relations for GenericForeignKey
            if field.is_relation and field.related_name is not None:
                field_name = field.get_accessor_name()
                if prefix:
                    field_path = f"{prefix}__{field_name}"
                else:
                    field_path = field_name
                    
                prefetch_fields.append(field_path)
    
    return prefetch_fields


def optimize_queryset(queryset, select_fields=None, prefetch_fields=None, defer_fields=None, only_fields=None):
    """
    Apply various optimization techniques to a queryset.
    
    This is a utility function that combines multiple optimization techniques in one call.
    
    Args:
        queryset: The Django queryset to optimize.
        select_fields (list): Fields to pass to select_related().
        prefetch_fields (list): Fields to pass to prefetch_related().
        defer_fields (list): Fields to pass to defer().
        only_fields (list): Fields to pass to only().
        
    Returns:
        QuerySet: The optimized queryset.
    """
    if select_fields:
        queryset = queryset.select_related(*select_fields)
        
    if prefetch_fields:
        queryset = queryset.prefetch_related(*prefetch_fields)
        
    if only_fields:
        queryset = queryset.only(*only_fields)
    elif defer_fields:
        queryset = queryset.defer(*defer_fields)
        
    return queryset


def get_model_field_names(model, include_relations=False):
    """
    Get a list of all field names for a model.
    
    This is useful for constructing only() or defer() calls when you want to
    include or exclude certain types of fields.
    
    Args:
        model: The Django model class.
        include_relations (bool): Whether to include relation fields.
        
    Returns:
        list: List of field names.
    """
    fields = []
    
    for field in model._meta.get_fields():
        # Skip reverse relations and relations if not requested
        if not include_relations and (field.is_relation or field.one_to_many or field.many_to_many):
            continue
            
        # Add direct field names
        if hasattr(field, 'name'):
            fields.append(field.name)
    
    return fields


def count_database_queries(func):
    """
    Decorator to count and print database queries executed in a function.
    
    This is a debugging utility useful for identifying and optimizing database-heavy code.
    
    Usage:
        @count_database_queries
        def my_view(request):
            # View code here
            
    Note:
        This decorator should only be used during development and debugging.
    """
    from functools import wraps
    from django.db import connection
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        initial_queries = len(connection.queries)
        
        # Enable query recording if it's not already enabled
        debug = connection.use_debug_cursor
        connection.use_debug_cursor = True
        
        # Call the original function
        result = func(*args, **kwargs)
        
        # Count queries
        final_queries = len(connection.queries)
        query_count = final_queries - initial_queries
        
        # Print query information
        print(f"Function {func.__name__} executed {query_count} queries")
        
        # Restore original debug setting
        connection.use_debug_cursor = debug
        
        return result
    
    return wrapper
