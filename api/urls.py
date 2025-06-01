from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)


urlpatterns = [
    # API Schema
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # API Documentation
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API Endpoints - sử dụng cấu trúc v1 đã có
    path('v1/', include('api.v1.urls')),
]
