from rest_framework import generics, filters
from rest_framework.permissions import IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from .models import SalesReport, ProductReport, CustomerReport, TrafficLog
from .serializers import (
    SalesReportSerializer, ProductReportSerializer,
    CustomerReportSerializer, TrafficLogSerializer
)


class SalesReportListView(generics.ListAPIView):
    """
    API view to list sales reports.
    Admin only access.
    """
    queryset = SalesReport.objects.all()
    serializer_class = SalesReportSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['date']
    ordering_fields = ['date', 'total_orders', 'total_revenue', 'net_revenue']
    ordering = ['-date']


class ProductReportListView(generics.ListAPIView):
    """
    API view to list product reports.
    Admin only access.
    """
    queryset = ProductReport.objects.all()
    serializer_class = ProductReportSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['last_sold_at']
    search_fields = ['product__name', 'product__description']
    ordering_fields = [
        'sold_quantity', 'total_revenue', 'average_rating',
        'last_sold_at', 'product__name'
    ]
    ordering = ['-sold_quantity']


class CustomerReportListView(generics.ListAPIView):
    """
    API view to list customer reports.
    Admin only access.
    """
    queryset = CustomerReport.objects.all()
    serializer_class = CustomerReportSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['last_order_at']
    search_fields = [
        'customer__user__email', 'customer__user__first_name',
        'customer__user__last_name', 'customer__phone_number'
    ]
    ordering_fields = [
        'total_orders', 'total_spent', 'average_order_value', 'last_order_at'
    ]
    ordering = ['-total_spent']


class TrafficLogListView(generics.ListAPIView):
    """
    API view to list traffic logs.
    Admin only access.
    """
    queryset = TrafficLog.objects.all()
    serializer_class = TrafficLogSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['method', 'endpoint']
    search_fields = ['endpoint', 'ip_address']
    ordering_fields = ['timestamp', 'duration_ms']
    ordering = ['-timestamp']
