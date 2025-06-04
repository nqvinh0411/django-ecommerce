from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import PaymentViewSet

# Legacy imports for backward compatibility
from .views import PaymentCheckoutView, PaymentStatusView

app_name = 'payments'

# Thiết lập router cho ViewSets
router = DefaultRouter(trailing_slash=False)
router.register(r'', PaymentViewSet, basename='payment')

urlpatterns = [
    # ViewSets URL patterns - Chuẩn hóa API
    path('', include(router.urls)),
    
    # ===== LEGACY ENDPOINTS FOR BACKWARD COMPATIBILITY =====
    # These endpoints are kept for backward compatibility but will be deprecated
    # Hãy sử dụng các endpoint mới từ router ở trên
    
    # Payment endpoints - DEPRECATED
    path('/old/checkout', PaymentCheckoutView.as_view(), name='payment-checkout-legacy'),
    path('/old/<int:pk>/status', PaymentStatusView.as_view(), name='payment-status-legacy'),
    
    # Note: Những URL patterns cũ này sẽ bị loại bỏ trong phiên bản tương lai
    # Vui lòng sử dụng các endpoints mới được cung cấp bởi router
]
