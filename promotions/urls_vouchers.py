from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import VoucherViewSet

app_name = 'vouchers'

# Tạo router cho Vouchers API
router = DefaultRouter()
router.register('', VoucherViewSet, basename='voucher')

urlpatterns = [
    # Sử dụng router URLs
    path('', include(router.urls)),
] 