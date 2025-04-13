from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated

from core.views.base import (
    BaseListView,
    BaseCreateView,
    BaseRetrieveUpdateDestroyView
)
from ..models import Salary
from ..serializers import SalarySerializer


class SalaryListView(BaseListView):
    """
    API endpoint để liệt kê các cấu trúc lương (GET).
    """
    queryset = Salary.objects.all()
    serializer_class = SalarySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'salary_type', 'currency', 'is_active']
    search_fields = ['notes', 'employee__first_name', 'employee__last_name']
    ordering_fields = ['employee__last_name', 'base_salary', 'effective_date']
    ordering = ['-effective_date']
    
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
        
        # Lọc theo phạm vi lương
        base_salary_min = self.request.query_params.get('base_salary_min')
        base_salary_max = self.request.query_params.get('base_salary_max')
        
        if base_salary_min:
            queryset = queryset.filter(base_salary__gte=base_salary_min)
        
        if base_salary_max:
            queryset = queryset.filter(base_salary__lte=base_salary_max)
        
        # Lọc theo phòng ban
        department_id = self.request.query_params.get('department_id')
        if department_id:
            queryset = queryset.filter(employee__department_id=department_id)
            
        return queryset


class SalaryCreateView(BaseCreateView):
    """
    API endpoint để tạo mới cấu trúc lương (POST).
    """
    serializer_class = SalarySerializer
    permission_classes = [IsAuthenticated]


class SalaryRetrieveUpdateDestroyView(BaseRetrieveUpdateDestroyView):
    """
    API endpoint để xem (GET), cập nhật (PUT/PATCH), hoặc xóa (DELETE) cấu trúc lương.
    """
    queryset = Salary.objects.all()
    serializer_class = SalarySerializer
    permission_classes = [IsAuthenticated]
