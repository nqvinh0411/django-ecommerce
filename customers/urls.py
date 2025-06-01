from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import (
    CustomerViewSet,
    CustomerGroupViewSet,
    CustomerAddressViewSet,
    CustomerActivityViewSet
)

app_name = 'customers'

# Thiết lập router cho ViewSets
router = DefaultRouter()
router.register(r'', CustomerViewSet, basename='customer')
router.register(r'groups', CustomerGroupViewSet, basename='customer-group')
router.register(r'addresses', CustomerAddressViewSet, basename='customer-address')
router.register(r'activities', CustomerActivityViewSet, basename='customer-activity')

# URL patterns cho router
urlpatterns = [
    # ViewSets URL patterns - API chuẩn hóa
    path('', include(router.urls)),
]
