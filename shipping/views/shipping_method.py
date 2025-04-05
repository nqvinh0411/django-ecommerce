"""
Shipping Method views module
"""
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from core.views.base import BaseListView, BaseCreateView, BaseRetrieveView, BaseUpdateView, BaseDestroyView
from ..models import ShippingMethod
from ..serializers import ShippingMethodSerializer
from ..permissions import IsAdminUserOrReadOnly


class ShippingMethodListView(BaseListView):
    """
    API để liệt kê tất cả các phương thức vận chuyển.
    GET /shipping/methods
    """
    queryset = ShippingMethod.objects.all()
    serializer_class = ShippingMethodSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'estimated_days']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'base_fee', 'estimated_days', 'created_at']
    ordering = ['name']


class ShippingMethodCreateView(BaseCreateView):
    """
    API để tạo mới phương thức vận chuyển.
    POST /shipping/methods/create
    """
    queryset = ShippingMethod.objects.all()
    serializer_class = ShippingMethodSerializer
    permission_classes = [IsAdminUserOrReadOnly]


class ShippingMethodRetrieveView(BaseRetrieveView):
    """
    API để xem chi tiết một phương thức vận chuyển.
    GET /shipping/methods/{id}
    """
    queryset = ShippingMethod.objects.all()
    serializer_class = ShippingMethodSerializer
    permission_classes = [IsAdminUserOrReadOnly]


class ShippingMethodUpdateView(BaseUpdateView):
    """
    API để cập nhật một phương thức vận chuyển.
    PUT/PATCH /shipping/methods/{id}/update
    """
    queryset = ShippingMethod.objects.all()
    serializer_class = ShippingMethodSerializer
    permission_classes = [IsAdminUserOrReadOnly]


class ShippingMethodDestroyView(BaseDestroyView):
    """
    API để xóa một phương thức vận chuyển.
    DELETE /shipping/methods/{id}/delete
    """
    queryset = ShippingMethod.objects.all()
    serializer_class = ShippingMethodSerializer
    permission_classes = [IsAdminUserOrReadOnly]
