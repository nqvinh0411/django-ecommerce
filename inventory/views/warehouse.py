from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import IsAdminUser

from core.views.base import BaseListView, BaseCreateView, BaseRetrieveView, BaseUpdateView, BaseDestroyView
from ..models import Warehouse
from ..serializers import WarehouseSerializer


class WarehouseListView(BaseListView):
    """
    API endpoint để liệt kê tất cả kho hàng (GET).
    Chỉ admin mới có thể tạo, cập nhật hoặc xóa kho hàng.
    """
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_default', 'is_active']
    search_fields = ['name', 'location', 'description']
    ordering_fields = ['name', 'location', 'created_at']
    ordering = ['name']


class WarehouseCreateView(BaseCreateView):
    """
    API endpoint để tạo mới một kho hàng (POST).
    Chỉ admin mới có thể tạo, cập nhật hoặc xóa kho hàng.
    """
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsAdminUser]
    
    def perform_create(self, serializer):
        # Nếu đánh dấu là kho mặc định, cập nhật các kho khác
        if serializer.validated_data.get('is_default', False):
            Warehouse.objects.filter(is_default=True).update(is_default=False)
        serializer.save()


class WarehouseRetrieveView(BaseRetrieveView):
    """
    API endpoint để xem (GET) một kho hàng.
    Chỉ admin mới có thể tạo, cập nhật hoặc xóa kho hàng.
    """
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsAdminUser]


class WarehouseUpdateView(BaseUpdateView):
    """
    API endpoint để cập nhật (PUT/PATCH) một kho hàng.
    Chỉ admin mới có thể tạo, cập nhật hoặc xóa kho hàng.
    """
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsAdminUser]
    
    def perform_update(self, serializer):
        # Nếu đánh dấu là kho mặc định, cập nhật các kho khác
        if serializer.validated_data.get('is_default', False) and not self.get_object().is_default:
            Warehouse.objects.filter(is_default=True).update(is_default=False)
        serializer.save()


class WarehouseDestroyView(BaseDestroyView):
    """
    API endpoint để xóa (DELETE) một kho hàng.
    Chỉ admin mới có thể tạo, cập nhật hoặc xóa kho hàng.
    """
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsAdminUser]
