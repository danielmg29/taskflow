"""
Schema Introspection System

This module extracts complete schema information from Django models
and provides it to the frontend via API endpoints.

This enables:
- Automatic form generation
- Type-safe operations
- Self-documenting APIs
- Zero frontend/backend schema drift
"""

from django.apps import apps
from django.db.models import Model
from django.db.models.fields.related import ForeignKey, ManyToManyField, OneToOneField
from typing import Dict, Any, List, Type, Optional


def get_field_type(field) -> str:
    """
    Get human-readable field type.
    
    Django's internal types (CharField, IntegerField, etc.) are converted
    to consistent string representations that the frontend can understand.
    """
    field_class_name = field.__class__.__name__
    
    # Map Django field types to frontend-friendly names
    type_mapping = {
        'AutoField': 'auto',
        'BigAutoField': 'auto',
        'CharField': 'string',
        'TextField': 'text',
        'IntegerField': 'integer',
        'BigIntegerField': 'integer',
        'PositiveIntegerField': 'integer',
        'SmallIntegerField': 'integer',
        'FloatField': 'float',
        'DecimalField': 'decimal',
        'BooleanField': 'boolean',
        'DateField': 'date',
        'DateTimeField': 'datetime',
        'TimeField': 'time',
        'EmailField': 'email',
        'URLField': 'url',
        'SlugField': 'slug',
        'UUIDField': 'uuid',
        'FileField': 'file',
        'ImageField': 'image',
        'JSONField': 'json',
        'ForeignKey': 'foreignkey',
        'OneToOneField': 'onetoone',
        'ManyToManyField': 'manytomany',
    }
    
    return type_mapping.get(field_class_name, field_class_name.lower())


def get_field_schema(field) -> Dict[str, Any]:
    """
    Extract complete schema information for a single field.
    
    Returns all information the frontend needs to:
    - Render appropriate input widget
    - Validate user input
    - Display help text
    - Handle relationships
    """
    # Base field information
    field_info = {
        'name': field.name,
        'type': get_field_type(field),
        'required': not field.null and not field.blank and not field.has_default(),
        'label': field.verbose_name.capitalize() if hasattr(field, 'verbose_name') else field.name.replace('_', ' ').title(),
        'help_text': field.help_text if field.help_text else None,
    }
    
    # Check if this is a relationship field
    if isinstance(field, (ForeignKey, OneToOneField, ManyToManyField)):
        field_info.update({
            'related_model': field.related_model.__name__,
            'many': isinstance(field, ManyToManyField),
        })
    else:
        # Regular field attributes
        
        # Max length (for strings)
        if hasattr(field, 'max_length') and field.max_length:
            field_info['max_length'] = field.max_length
        
        # Choices (for select dropdowns)
        if hasattr(field, 'choices') and field.choices:
            field_info['choices'] = [
                {'value': choice[0], 'label': choice[1]}
                for choice in field.choices
            ]
        
        # Default value
        if field.has_default():
            default = field.get_default()
            # Make sure default is JSON serializable
            if callable(default):
                field_info['default'] = None
            elif isinstance(default, (str, int, float, bool, type(None))):
                field_info['default'] = default
            else:
                field_info['default'] = str(default)
        else:
            field_info['default'] = None
        
        # Numeric field constraints
        if hasattr(field, 'max_digits'):
            field_info['max_digits'] = field.max_digits
        if hasattr(field, 'decimal_places'):
            field_info['decimal_places'] = field.decimal_places
        
        # Unique constraint
        if hasattr(field, 'unique'):
            field_info['unique'] = field.unique
    
    return field_info


def get_model_schema(model_class: Type[Model]) -> Dict[str, Any]:
    """
    Extract complete schema information from a Django model.
    
    This is the heart of schema introspection. Given any model class,
    it returns everything the frontend needs to work with that model.
    
    Args:
        model_class: Any Django Model class
        
    Returns:
        Complete schema including:
        - Model metadata (name, verbose names)
        - All fields with full specifications
        - Relationships to other models
    """
    fields_schema = []
    
    # Iterate through all fields in the model
    for field in model_class._meta.get_fields():
        # Skip reverse relations (we only care about forward relations)
        if field.auto_created and not field.concrete:
            continue
        
        # Get schema for this field
        field_schema = get_field_schema(field)
        fields_schema.append(field_schema)
    
    # Build complete model schema
    return {
        'model_name': model_class.__name__,
        'app_label': model_class._meta.app_label,
        'table_name': model_class._meta.db_table,
        'verbose_name': str(model_class._meta.verbose_name),
        'verbose_name_plural': str(model_class._meta.verbose_name_plural),
        'fields': fields_schema,
    }


def get_all_models_schema(app_label: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """
    Get schemas for all registered models, optionally filtered by app.
    
    Args:
        app_label: Optional app name to filter (e.g., 'tasks')
                   If None, returns all models
    
    Returns:
        Dictionary mapping model names to their schemas:
        {
            'Task': {schema},
            'Project': {schema},
            ...
        }
    """
    schemas = {}
    
    # Get all models
    models = apps.get_models()
    
    # Filter by app if specified
    if app_label:
        models = [m for m in models if m._meta.app_label == app_label]
    
    # Generate schema for each model
    for model in models:
        # Skip abstract models
        if model._meta.abstract:
            continue
        
        # Skip Django's built-in models (auth, contenttypes, etc.)
        # We only want user-defined models
        if model._meta.app_label in ['auth', 'contenttypes', 'sessions', 'admin']:
            continue
        
        schemas[model.__name__] = get_model_schema(model)
    
    return schemas


def get_model_by_name(model_name: str, app_label: Optional[str] = None) -> Optional[Type[Model]]:
    """
    Get a model class by its name.
    
    Useful for dynamic model access in views.
    
    Args:
        model_name: Name of the model (e.g., 'Task')
        app_label: Optional app label (e.g., 'tasks')
        
    Returns:
        Model class or None if not found
    """
    try:
        if app_label:
            return apps.get_model(app_label, model_name)
        else:
            # Search all apps
            for model in apps.get_models():
                if model.__name__ == model_name:
                    return model
            return None
    except LookupError:
        return None


def validate_model_access(model_name: str, allowed_models: Optional[List[str]] = None) -> bool:
    """
    Validate that a model is allowed to be accessed via API.
    
    Security function to whitelist which models can be accessed dynamically.
    
    Args:
        model_name: Name of the model to check
        allowed_models: List of allowed model names
                        If None, all models are allowed (development only!)
        
    Returns:
        True if model is allowed, False otherwise
    """
    if allowed_models is None:
        # WARNING: In production, you should ALWAYS specify allowed_models
        return True
    
    return model_name in allowed_models