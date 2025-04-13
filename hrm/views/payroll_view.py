from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated

from core.views.base import (
    BaseListView,
    BaseCreateView,
    BaseRetrieveUpdateDestroyView
)
from ..models import Payroll
from ..serializers import PayrollSerializer


class PayrollListView(BaseListView):
    """
    API endpoint để liệt kê các bảng lương (GET).
    """
    queryset = Payroll.objects.all()
    serializer_class = PayrollSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'status', 'payment_method', 'payroll_period']
    search_fields = ['notes', 'payment_reference', 'employee__first_name', 'employee__last_name']
    ordering_fields = ['employee__last_name', 'payroll_period', 'payment_date', 'net_amount']
    ordering = ['-payroll_period', 'employee__last_name']
    
    def get_queryset(self):
        """Tùy chỉnh queryset dựa trên tham số yêu cầu."""
        queryset = super().get_queryset()
        
        # Lọc theo phạm vi ngày kỳ lương
        start_from = self.request.query_params.get('start_from')
        start_to = self.request.query_params.get('start_to')
        
        if start_from:
            queryset = queryset.filter(start_date__gte=start_from)
        
        if start_to:
            queryset = queryset.filter(end_date__lte=start_to)
        
        # Lọc theo ngày thanh toán
        payment_from = self.request.query_params.get('payment_from')
        payment_to = self.request.query_params.get('payment_to')
        
        if payment_from:
            queryset = queryset.filter(payment_date__gte=payment_from)
        
        if payment_to:
            queryset = queryset.filter(payment_date__lte=payment_to)
        
        # Lọc theo phạm vi tiền lương
        amount_min = self.request.query_params.get('amount_min')
        amount_max = self.request.query_params.get('amount_max')
        
        if amount_min:
            queryset = queryset.filter(net_amount__gte=amount_min)
        
        if amount_max:
            queryset = queryset.filter(net_amount__lte=amount_max)
        
        # Lọc theo phòng ban
        department_id = self.request.query_params.get('department_id')
        if department_id:
            queryset = queryset.filter(employee__department_id=department_id)
            
        return queryset


class PayrollCreateView(BaseCreateView):
    """
    API endpoint để tạo mới bảng lương (POST).
    """
    serializer_class = PayrollSerializer
    permission_classes = [IsAuthenticated]


class PayrollRetrieveUpdateDestroyView(BaseRetrieveUpdateDestroyView):
    """
    API endpoint để xem (GET), cập nhật (PUT/PATCH), hoặc xóa (DELETE) bảng lương.
    """
    queryset = Payroll.objects.all()
    serializer_class = PayrollSerializer
    permission_classes = [IsAuthenticated]
