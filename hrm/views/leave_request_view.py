from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated

from core.views.base import (
    BaseListView,
    BaseCreateView,
    BaseRetrieveUpdateDestroyView
)
from ..models import LeaveRequest
from ..serializers import LeaveRequestSerializer


class LeaveRequestListView(BaseListView):
    """
    API endpoint để liệt kê các đơn xin nghỉ phép (GET).
    """
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'leave_type', 'status', 'half_day']
    search_fields = ['reason', 'reviewer_comments', 'employee__first_name', 'employee__last_name']
    ordering_fields = ['start_date', 'end_date', 'status', 'employee__last_name', 'created_at']
    ordering = ['-start_date']
    
    def get_queryset(self):
        """Tùy chỉnh queryset dựa trên tham số yêu cầu."""
        queryset = super().get_queryset()
        
        # Lọc theo phạm vi ngày
        start_from = self.request.query_params.get('start_from')
        start_to = self.request.query_params.get('start_to')
        
        if start_from:
            queryset = queryset.filter(start_date__gte=start_from)
        
        if start_to:
            queryset = queryset.filter(start_date__lte=start_to)
        
        # Lọc theo người duyệt
        reviewed_by_id = self.request.query_params.get('reviewed_by_id')
        if reviewed_by_id:
            queryset = queryset.filter(reviewed_by_id=reviewed_by_id)
        
        # Lọc theo phòng ban
        department_id = self.request.query_params.get('department_id')
        if department_id:
            queryset = queryset.filter(employee__department_id=department_id)
            
        return queryset


class LeaveRequestCreateView(BaseCreateView):
    """
    API endpoint để tạo mới đơn xin nghỉ phép (POST).
    """
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]


class LeaveRequestRetrieveUpdateDestroyView(BaseRetrieveUpdateDestroyView):
    """
    API endpoint để xem (GET), cập nhật (PUT/PATCH), hoặc xóa (DELETE) đơn xin nghỉ phép.
    """
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]
