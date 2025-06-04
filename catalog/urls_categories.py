from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import CategoryViewSet

app_name = 'categories'

# Tạo router cho Categories API
router = DefaultRouter(trailing_slash=False)
router.register('', CategoryViewSet, basename='category')

urlpatterns = [
    # Sử dụng router URLs
    path('', include(router.urls)),
] 