from django.urls import path
from . import views

app_name = 'promotions'

urlpatterns = [
    # Coupon endpoints
    path('coupons', views.CouponListCreateView.as_view(), name='coupon-list'),
    path('coupons/<int:pk>', views.CouponDetailView.as_view(), name='coupon-detail'),
    
    # Campaign endpoints
    path('campaigns', views.PromotionCampaignListView.as_view(), name='campaign-list'),
    path('campaigns/admin', views.PromotionCampaignAdminListCreateView.as_view(), name='campaign-admin-list'),
    path('campaigns/<int:pk>', views.PromotionCampaignDetailView.as_view(), name='campaign-detail'),
    
    # Voucher endpoints
    path('vouchers', views.CustomerVoucherListView.as_view(), name='voucher-list'),
    path('vouchers/<int:pk>', views.VoucherDetailView.as_view(), name='voucher-detail'),
    
    # Apply promotion endpoints
    path('coupons/apply', views.ApplyCouponView.as_view(), name='coupon-apply'),
    path('vouchers/apply', views.ApplyVoucherView.as_view(), name='voucher-apply'),
    
    # Usage logs
    path('usage-logs', views.UsageLogListView.as_view(), name='usage-log-list'),
]
