from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated

from core.views.base import (
    BaseListView,
    BaseCreateView,
    BaseRetrieveUpdateDestroyView
)
from ..models import Employee
from ..serializers import EmployeeSerializer


class EmployeeListView(BaseListView):
    """
    API endpoint for listing employees (GET).
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'position', 'employment_status', 'is_active']
    search_fields = ['first_name', 'last_name', 'employee_id', 'email', 'phone']
    ordering_fields = ['last_name', 'first_name', 'employee_id', 'hire_date', 'department__name']
    ordering = ['last_name', 'first_name']
    
    def get_queryset(self):
        """Customize queryset based on request parameters."""
        queryset = super().get_queryset()
        
        # Filter by supervisor
        supervisor_id = self.request.query_params.get('supervisor_id')
        if supervisor_id:
            queryset = queryset.filter(supervisor_id=supervisor_id)
        
        # Filter by hire date range
        hire_date_from = self.request.query_params.get('hire_date_from')
        hire_date_to = self.request.query_params.get('hire_date_to')
        
        if hire_date_from:
            queryset = queryset.filter(hire_date__gte=hire_date_from)
        
        if hire_date_to:
            queryset = queryset.filter(hire_date__lte=hire_date_to)
            
        return queryset


class EmployeeCreateView(BaseCreateView):
    """
    API endpoint for creating a new employee (POST).
    """
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]


class EmployeeRetrieveUpdateDestroyView(BaseRetrieveUpdateDestroyView):
    """
    API endpoint for retrieving (GET), updating (PUT/PATCH), or deleting (DELETE) an employee.
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]
