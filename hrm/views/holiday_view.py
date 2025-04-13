from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from core.views.base import (
    BaseListView,
    BaseCreateView,
    BaseRetrieveUpdateDestroyView
)
from ..models import Holiday
from ..serializers import HolidaySerializer


class HolidayListView(BaseListView):
    """
    API endpoint để liệt kê các ngày nghỉ/lễ (GET).
    """
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['holiday_type', 'is_paid', 'recurring']
    search_fields = ['name', 'description']
    ordering_fields = ['date', 'name']
    ordering = ['date']
    
    def get_queryset(self):
        """Tùy chỉnh queryset dựa trên tham số yêu cầu."""
        queryset = super().get_queryset()
        
        # Lọc theo phạm vi ngày
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
            
        # Lọc theo phòng ban
        department_id = self.request.query_params.get('department_id')
        if department_id:
            queryset = queryset.filter(
                Q(applicable_departments__id=department_id) | 
                Q(applicable_departments__isnull=True)
            )
            
        return queryset


class HolidayCreateView(BaseCreateView):
    """
    API endpoint để tạo mới ngày nghỉ/lễ (POST).
    """
    serializer_class = HolidaySerializer
    permission_classes = [IsAuthenticated]


class HolidayRetrieveUpdateDestroyView(BaseRetrieveUpdateDestroyView):
    """
    API endpoint để xem (GET), cập nhật (PUT/PATCH), hoặc xóa (DELETE) ngày nghỉ/lễ.
    """
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    permission_classes = [IsAuthenticated]
