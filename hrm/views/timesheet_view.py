from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated

from core.views.base import (
    BaseListView,
    BaseCreateView,
    BaseRetrieveUpdateDestroyView
)
from ..models import Timesheet
from ..serializers import TimesheetSerializer


class TimesheetListView(BaseListView):
    """
    API endpoint để liệt kê bảng chấm công (GET).
    """
    queryset = Timesheet.objects.all()
    serializer_class = TimesheetSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'status']
    search_fields = ['notes', 'employee__first_name', 'employee__last_name']
    ordering_fields = ['date', 'check_in', 'employee__last_name']
    ordering = ['-date', '-check_in']
    
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
        
        # Lọc theo thời gian check-in
        check_in_from = self.request.query_params.get('check_in_from')
        check_in_to = self.request.query_params.get('check_in_to')
        
        if check_in_from:
            queryset = queryset.filter(check_in__gte=check_in_from)
        
        if check_in_to:
            queryset = queryset.filter(check_in__lte=check_in_to)
        
        # Lọc theo phòng ban
        department_id = self.request.query_params.get('department_id')
        if department_id:
            queryset = queryset.filter(employee__department_id=department_id)
            
        return queryset


class TimesheetCreateView(BaseCreateView):
    """
    API endpoint để tạo mới bảng chấm công (POST).
    """
    serializer_class = TimesheetSerializer
    permission_classes = [IsAuthenticated]


class TimesheetRetrieveUpdateDestroyView(BaseRetrieveUpdateDestroyView):
    """
    API endpoint để xem (GET), cập nhật (PUT/PATCH), hoặc xóa (DELETE) bảng chấm công.
    """
    queryset = Timesheet.objects.all()
    serializer_class = TimesheetSerializer
    permission_classes = [IsAuthenticated]
