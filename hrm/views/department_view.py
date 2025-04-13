from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated

from core.views.base import (
    BaseListView,
    BaseCreateView,
    BaseRetrieveUpdateDestroyView
)
from ..models import Department
from ..serializers import DepartmentSerializer


class DepartmentListView(BaseListView):
    """
    API endpoint for listing departments (GET).
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'parent']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        """Customize queryset based on request parameters."""
        queryset = super().get_queryset()
        
        # Filter by manager ID
        manager_id = self.request.query_params.get('manager_id')
        if manager_id:
            queryset = queryset.filter(manager_id=manager_id)
            
        return queryset


class DepartmentCreateView(BaseCreateView):
    """
    API endpoint for creating a new department (POST).
    """
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]


class DepartmentRetrieveUpdateDestroyView(BaseRetrieveUpdateDestroyView):
    """
    API endpoint for retrieving (GET), updating (PUT/PATCH), or deleting (DELETE) a department.
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
