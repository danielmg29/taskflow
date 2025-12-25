"""
Generic Repository Pattern - Functional Approach

This module provides a factory function that generates CRUD operations
for any Django model. This eliminates the need to write repetitive
ViewSets and Serializers for each model.

Key Insight: Most CRUD operations are identical across models.
Why write them 100 times?
"""

from typing import Type, TypeVar, Optional, Dict, Any, List
from django.db.models import Model, QuerySet
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError

# Type variable for generic model typing
T = TypeVar('T', bound=Model)


def create_repository(model_class: Type[T]):
    """
    Factory function that returns a dictionary of repository functions
    for ANY Django model.
    
    This is the heart of the Zero-Redundancy Principle:
    - Write once
    - Use for all models
    - Pure functions (easy to test)
    - No class overhead
    
    Args:
        model_class: Any Django Model class (Task, Project, etc.)
        
    Returns:
        Dictionary of CRUD functions:
        {
            'get_all': function,
            'get_by_id': function,
            'create': function,
            'update': function,
            'delete': function
        }
    """
    
    def get_all(
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[List[str]] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """
        Retrieve all instances with optional filtering, ordering, and pagination.
        
        Args:
            filters: Django ORM filter kwargs (e.g., {'status': 'active'})
            order_by: List of fields to order by (e.g., ['-created_at'])
            page: Page number (1-indexed)
            page_size: Items per page
            
        Returns:
            {
                'data': List of model instances as dicts,
                'page': Current page number,
                'total_pages': Total pages,
                'total_count': Total items
            }
        """
        # Start with all objects
        queryset = model_class.objects.all()
        
        # Apply filters if provided
        if filters:
            queryset = queryset.filter(**filters)
        
        # Apply ordering if provided
        if order_by:
            queryset = queryset.order_by(*order_by)
        
        # Paginate
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        return {
            'data': list(page_obj.object_list.values()),
            'page': page,
            'total_pages': paginator.num_pages,
            'total_count': paginator.count
        }
    
    def get_by_id(id: int) -> Optional[T]:
        """
        Retrieve a single instance by ID.
        
        Args:
            id: Primary key of the instance
            
        Returns:
            Model instance or None if not found
        """
        try:
            return model_class.objects.get(pk=id)
        except model_class.DoesNotExist:
            return None
    
    def create(data: Dict[str, Any]) -> T:
        """
        Create a new instance.
        
        Args:
            data: Dictionary of field values
            
        Returns:
            Created model instance
            
        Raises:
            ValidationError: If data doesn't pass model validation
        """
        instance = model_class(**data)
        instance.full_clean()  # Validate before saving
        instance.save()
        return instance
    
    def update(id: int, data: Dict[str, Any]) -> Optional[T]:
        """
        Update an existing instance.
        
        Args:
            id: Primary key of instance to update
            data: Dictionary of fields to update
            
        Returns:
            Updated instance or None if not found
            
        Raises:
            ValidationError: If data doesn't pass validation
        """
        instance = get_by_id(id)
        if not instance:
            return None
        
        # Update fields
        for key, value in data.items():
            setattr(instance, key, value)
        
        instance.full_clean()  # Validate
        instance.save()
        return instance
    
    def delete(id: int) -> bool:
        """
        Delete an instance.
        
        Args:
            id: Primary key of instance to delete
            
        Returns:
            True if deleted, False if not found
        """
        instance = get_by_id(id)
        if not instance:
            return False
        
        instance.delete()
        return True
    
    # Return all functions as a dictionary
    return {
        'get_all': get_all,
        'get_by_id': get_by_id,
        'create': create,
        'update': update,
        'delete': delete
    }