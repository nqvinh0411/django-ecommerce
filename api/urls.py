from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)


urlpatterns = [
    # API Schema & Documentation
    path('schema', SpectacularAPIView.as_view(), name='schema'),
    path('docs', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API version routing
    path('auth', include(('users.urls', 'users'), namespace='users')),

    path('v1', include(('api.v1.urls', 'v1'), namespace='v1')),
    # path('v2/', include(('api.v2.urls', 'v2')), namespace='v2'),
]
