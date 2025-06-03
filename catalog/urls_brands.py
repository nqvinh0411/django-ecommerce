from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import BrandViewSet

app_name = 'brands'

# Tạo router cho Brands API
router = DefaultRouter()
router.register('', BrandViewSet, basename='brand')

urlpatterns = [
    # Sử dụng router URLs
    path('', include(router.urls)),
] 