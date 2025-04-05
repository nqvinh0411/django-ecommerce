"""
Shipping Zone views module
"""
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from core.views.base import BaseListView, BaseCreateView, BaseRetrieveView, BaseUpdateView, BaseDestroyView
from ..models import ShippingZone
from ..serializers import ShippingZoneSerializer
from ..permissions import IsAdminUserOrReadOnly


class ShippingZoneListView(BaseListView):
    """
    API để liệt kê tất cả các vùng vận chuyển.
    GET /shipping/zones
    """
    queryset = ShippingZone.objects.all()
    serializer_class = ShippingZoneSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'countries', 'provinces']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class ShippingZoneCreateView(BaseCreateView):
    """
    API để tạo mới vùng vận chuyển.
    POST /shipping/zones/create
    """
    queryset = ShippingZone.objects.all()
    serializer_class = ShippingZoneSerializer
    permission_classes = [IsAdminUserOrReadOnly]


class ShippingZoneRetrieveView(BaseRetrieveView):
    """
    API để xem chi tiết một vùng vận chuyển.
    GET /shipping/zones/{id}
    """
    queryset = ShippingZone.objects.all()
    serializer_class = ShippingZoneSerializer
    permission_classes = [IsAdminUserOrReadOnly]


class ShippingZoneUpdateView(BaseUpdateView):
    """
    API để cập nhật một vùng vận chuyển.
    PUT/PATCH /shipping/zones/{id}/update
    """
    queryset = ShippingZone.objects.all()
    serializer_class = ShippingZoneSerializer
    permission_classes = [IsAdminUserOrReadOnly]


class ShippingZoneDestroyView(BaseDestroyView):
    """
    API để xóa một vùng vận chuyển.
    DELETE /shipping/zones/{id}/delete
    """
    queryset = ShippingZone.objects.all()
    serializer_class = ShippingZoneSerializer
    permission_classes = [IsAdminUserOrReadOnly]
