from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import AttributeValueViewSet

app_name = 'attribute_values'

# Tạo router cho Attribute Values API
router = DefaultRouter(trailing_slash=False)
router.register('', AttributeValueViewSet, basename='attribute-value')

urlpatterns = [
    # Sử dụng router URLs
    path('', include(router.urls)),
] 