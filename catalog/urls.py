from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import (
    CategoryViewSet,
    BrandViewSet,
    TagViewSet,
    AttributeViewSet,
    AttributeValueViewSet
)

app_name = 'catalog'

# Tạo router cho Catalog API
router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('brands', BrandViewSet, basename='brand')
router.register('tags', TagViewSet, basename='tag')
router.register('attributes', AttributeViewSet, basename='attribute')
router.register('attribute-values', AttributeValueViewSet, basename='attribute-value')

urlpatterns = [
    # Sử dụng router URLs
    path('', include(router.urls)),
]
