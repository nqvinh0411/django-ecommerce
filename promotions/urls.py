from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import (
    CouponViewSet,
    PromotionCampaignViewSet,
    VoucherViewSet,
    UsageLogViewSet
)

app_name = 'promotions'

# Tạo router cho Promotions API
router = DefaultRouter()
router.register('coupons', CouponViewSet, basename='coupon')
router.register('campaigns', PromotionCampaignViewSet, basename='campaign')
router.register('vouchers', VoucherViewSet, basename='voucher')
router.register('usage-logs', UsageLogViewSet, basename='usage-log')

urlpatterns = [
    # Sử dụng router URLs
    path('', include(router.urls)),
]
