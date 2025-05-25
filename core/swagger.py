"""
Cấu hình Swagger UI và ReDoc cho API Documentation.

Module này cung cấp các cấu hình và view cần thiết cho việc tích hợp
Swagger UI và ReDoc vào dự án để hiển thị tài liệu API.
"""
from django.urls import path, re_path
from django.conf import settings
from django.views.generic import TemplateView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

# Schema view cho API documentation
schema_view = get_schema_view(
    openapi.Info(
        title="E-commerce API",
        default_version='v1',
        description="API cho hệ thống E-commerce",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# URL patterns cho API documentation
api_doc_urls = [
    # Swagger UI
    re_path(
        r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json'
    ),
    path(
        'swagger/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
    
    # ReDoc
    path(
        'redoc/',
        schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'
    ),
    
    # Custom documentation page
    path(
        'docs/',
        TemplateView.as_view(
            template_name='api_docs/index.html',
            extra_context={'schema_url': 'schema-swagger-ui'}
        ),
        name='api-docs'
    ),
]
