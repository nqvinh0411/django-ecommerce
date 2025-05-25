from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import OrderViewSet

# Legacy imports for backward compatibility
from .views import (
    OrderCreateView, UserOrderListView, OrderDetailView, 
    OrderStatusUpdateView
)

app_name = 'orders'

# Thiết lập router cho ViewSets
router = DefaultRouter()
router.register(r'', OrderViewSet, basename='order')

urlpatterns = [
    # ViewSets URL patterns - Chuẩn hóa API
    path('', include(router.urls)),
    
    # ===== LEGACY ENDPOINTS FOR BACKWARD COMPATIBILITY =====
    # These endpoints are kept for backward compatibility but will be deprecated
    # Hãy sử dụng các endpoint mới từ router ở trên
    
    # Order endpoints - DEPRECATED
    path('/old', UserOrderListView.as_view(), name='order-list-legacy'),
    path('/old/create', OrderCreateView.as_view(), name='order-create-legacy'),
    path('/old/<int:order_id>', OrderDetailView.as_view(), name='order-detail-legacy'),
    path('/old/<int:order_id>/status', OrderStatusUpdateView.as_view(), name='order-status-update-legacy'),
    
    # Note: Những URL patterns cũ này sẽ bị loại bỏ trong phiên bản tương lai
    # Vui lòng sử dụng các endpoints mới được cung cấp bởi router
]
