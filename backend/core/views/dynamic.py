"""
Dynamic Views - Schema API Endpoints

These views expose the schema introspection system via HTTP,
allowing the frontend to query model schemas dynamically.
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from core.schema.introspection import (
    get_model_schema,
    get_all_models_schema,
    get_model_by_name,
    validate_model_access
)

# Define which models can be accessed via API
# SECURITY: This whitelist prevents unauthorized model access
ALLOWED_MODELS = ['Task', 'Project', 'TeamMember', 'Tag']


@require_http_methods(["GET"])
def get_schema_view(request, model_name: str):
    """
    Get schema for a specific model.
    
    GET /api/schema/Task
    Returns: Complete schema for Task model
    """
    # Security check
    if not validate_model_access(model_name, ALLOWED_MODELS):
        return JsonResponse(
            {'error': f'Model {model_name} is not accessible'},
            status=403
        )
    
    # Get model class
    model_class = get_model_by_name(model_name)
    
    if not model_class:
        return JsonResponse(
            {'error': f'Model {model_name} not found'},
            status=404
        )
    
    # Generate and return schema
    schema = get_model_schema(model_class)
    return JsonResponse(schema)


@require_http_methods(["GET"])
def get_all_schemas_view(request):
    """
    Get schemas for all allowed models.
    
    GET /api/schema/all
    Returns: Dictionary of all model schemas
    """
    # Get all schemas, filtered by allowed models
    all_schemas = get_all_models_schema()
    
    # Filter to only allowed models
    filtered_schemas = {
        name: schema
        for name, schema in all_schemas.items()
        if name in ALLOWED_MODELS
    }
    
    return JsonResponse(filtered_schemas)


@require_http_methods(["GET"])
def health_check(request):
    """
    Simple health check endpoint.
    
    GET /api/health
    Returns: Server status
    """
    return JsonResponse({
        'status': 'ok',
        'message': 'TaskFlow API is running'
    })