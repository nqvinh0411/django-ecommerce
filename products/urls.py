from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import ProductViewSet

app_name = 'products'

# Thiết lập router cho ViewSets
router = DefaultRouter()
router.register(r'', ProductViewSet, basename='product')

urlpatterns = [
    # ViewSets URL patterns - API chuẩn hóa
    path('', include(router.urls)),
]
