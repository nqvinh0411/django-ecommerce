from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import (
    PageViewSet,
    BannerViewSet,
    MenuItemViewSet
)

app_name = "pages"

# Tạo router cho Pages API
router = DefaultRouter(trailing_slash=False)
router.register('', PageViewSet, basename='page')
router.register('banners', BannerViewSet, basename='banner')
router.register('menu-items', MenuItemViewSet, basename='menu-item')

urlpatterns = [
    # Sử dụng router URLs
    path('', include(router.urls)),
]
