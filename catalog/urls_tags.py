from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import TagViewSet

app_name = 'tags'

# Tạo router cho Tags API
router = DefaultRouter()
router.register('', TagViewSet, basename='tag')

urlpatterns = [
    # Sử dụng router URLs
    path('', include(router.urls)),
] 