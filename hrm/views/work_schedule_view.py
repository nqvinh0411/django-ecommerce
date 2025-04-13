from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated

from core.views.base import (
    BaseListView,
    BaseCreateView,
    BaseRetrieveUpdateDestroyView
)
from ..models import WorkSchedule
from ..serializers import WorkScheduleSerializer


class WorkScheduleListView(BaseListView):
    """
    API endpoint để liệt kê lịch làm việc (GET).
    """
    queryset = WorkSchedule.objects.all()
    serializer_class = WorkScheduleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'schedule_type', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'effective_date', 'department__name']
    ordering = ['name']
    
    def get_queryset(self):
        """Tùy chỉnh queryset dựa trên tham số yêu cầu."""
        queryset = super().get_queryset()
        
        # Lọc theo phạm vi ngày
        effective_from = self.request.query_params.get('effective_from')
        effective_to = self.request.query_params.get('effective_to')
        
        if effective_from:
            queryset = queryset.filter(effective_date__gte=effective_from)
        
        if effective_to:
            queryset = queryset.filter(effective_date__lte=effective_to)
            
        # Lọc theo ngày làm việc
        working_day = self.request.query_params.get('working_day')
        if working_day:
            queryset = queryset.filter(working_days__contains=[int(working_day)])
            
        return queryset


class WorkScheduleCreateView(BaseCreateView):
    """
    API endpoint để tạo mới lịch làm việc (POST).
    """
    serializer_class = WorkScheduleSerializer
    permission_classes = [IsAuthenticated]


class WorkScheduleRetrieveUpdateDestroyView(BaseRetrieveUpdateDestroyView):
    """
    API endpoint để xem (GET), cập nhật (PUT/PATCH), hoặc xóa (DELETE) lịch làm việc.
    """
    queryset = WorkSchedule.objects.all()
    serializer_class = WorkScheduleSerializer
    permission_classes = [IsAuthenticated]
