from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated

from core.views.base import (
    BaseListView,
    BaseCreateView,
    BaseRetrieveUpdateDestroyView
)
from ..models import Position
from ..serializers import PositionSerializer


class PositionListView(BaseListView):
    """
    API endpoint for listing positions (GET).
    """
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'is_active']
    search_fields = ['title', 'code', 'description', 'requirements']
    ordering_fields = ['title', 'department__name', 'created_at']
    ordering = ['title']
    
    def get_queryset(self):
        """Customize queryset based on request parameters."""
        queryset = super().get_queryset()
        
        # Filter by salary range
        min_salary = self.request.query_params.get('min_salary')
        max_salary = self.request.query_params.get('max_salary')
        
        if min_salary:
            queryset = queryset.filter(min_salary__gte=min_salary)
        
        if max_salary:
            queryset = queryset.filter(max_salary__lte=max_salary)
            
        return queryset


class PositionCreateView(BaseCreateView):
    """
    API endpoint for creating a new position (POST).
    """
    serializer_class = PositionSerializer
    permission_classes = [IsAuthenticated]


class PositionRetrieveUpdateDestroyView(BaseRetrieveUpdateDestroyView):
    """
    API endpoint for retrieving (GET), updating (PUT/PATCH), or deleting (DELETE) a position.
    """
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = [IsAuthenticated]
