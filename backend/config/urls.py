"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from core.views.dynamic import (
    get_schema_view,
    get_all_schemas_view,
    health_check
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Health check
    path('api/health/', health_check, name='health_check'),
    
    # Schema introspection endpoints
    path('api/schema/<str:model_name>/', get_schema_view, name='get_schema'),
    path('api/schema/all/', get_all_schemas_view, name='get_all_schemas'),
    
    # Dynamic CRUD endpoints (we'll add these next phase)
    # path('api/<str:model_name>/', dynamic_crud_handler),
    # path('api/<str:model_name>/<int:pk>/', dynamic_detail_handler),
]
