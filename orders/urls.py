from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import OrderViewSet

app_name = 'orders'

# Thiết lập router cho ViewSets
router = DefaultRouter()
router.register(r'', OrderViewSet, basename='order')

urlpatterns = [
    # ViewSets URL patterns - API chuẩn hóa
    path('', include(router.urls)),
]
