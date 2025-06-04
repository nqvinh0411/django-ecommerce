from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import CouponViewSet

app_name = 'coupons'

# Tạo router cho Coupons API
router = DefaultRouter(trailing_slash=False)
router.register('', CouponViewSet, basename='coupon')

urlpatterns = [
    # Sử dụng router URLs
    path('', include(router.urls)),
]