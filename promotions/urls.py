from django.urls import path
from . import views

app_name = 'promotions'

urlpatterns = [
    # Coupon endpoints
    path('coupons', views.CouponListView.as_view(), name='coupon-list'),
    path('coupons/create', views.CouponCreateView.as_view(), name='coupon-create'),
    path('coupons/<int:pk>', views.CouponRetrieveView.as_view(), name='coupon-detail'),
    path('coupons/<int:pk>/update', views.CouponUpdateView.as_view(), name='coupon-update'),
    path('coupons/<int:pk>/delete', views.CouponDestroyView.as_view(), name='coupon-delete'),
    path('coupons/apply', views.ApplyCouponView.as_view(), name='coupon-apply'),
    
    # Campaign endpoints
    path('campaigns', views.PromotionCampaignListView.as_view(), name='campaign-list'),
    path('campaigns/admin', views.PromotionCampaignAdminListView.as_view(), name='campaign-admin-list'),
    path('campaigns/create', views.PromotionCampaignCreateView.as_view(), name='campaign-create'),
    path('campaigns/<int:pk>', views.PromotionCampaignRetrieveView.as_view(), name='campaign-detail'),
    path('campaigns/<int:pk>/update', views.PromotionCampaignUpdateView.as_view(), name='campaign-update'),
    path('campaigns/<int:pk>/delete', views.PromotionCampaignDestroyView.as_view(), name='campaign-delete'),
    
    # Voucher endpoints
    path('vouchers', views.CustomerVoucherListView.as_view(), name='voucher-list'),
    path('vouchers/<int:pk>', views.VoucherRetrieveView.as_view(), name='voucher-detail'),
    path('vouchers/apply', views.ApplyVoucherView.as_view(), name='voucher-apply'),
    
    # Usage logs
    path('usage-logs', views.UsageLogListView.as_view(), name='usage-log-list'),
]
