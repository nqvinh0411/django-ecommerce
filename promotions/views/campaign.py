"""
Promotion Campaign views module
"""
from django.utils import timezone
from django.db.models import Q
from rest_framework import filters
from rest_framework.permissions import IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend

from core.views.base import BaseListView, BaseCreateView, BaseRetrieveView, BaseUpdateView, BaseDestroyView
from ..models import PromotionCampaign
from ..serializers import PromotionCampaignSerializer


class PromotionCampaignListView(BaseListView):
    """
    API để liệt kê các chiến dịch khuyến mãi đang hoạt động.
    GET /promotions/campaigns
    
    Đây là endpoint công khai, chỉ hiển thị các chiến dịch đang hoạt động.
    """
    serializer_class = PromotionCampaignSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'start_date', 'end_date']
    ordering = ['-start_date']
    
    def get_queryset(self):
        """
        Filter campaigns to show only active ones with valid dates.
        """
        now = timezone.now()
        return PromotionCampaign.objects.filter(
            is_active=True,
            start_date__lte=now
        ).filter(
            # No end_date or end_date is in the future
            Q(end_date__isnull=True) | Q(end_date__gt=now)
        )


class PromotionCampaignAdminListView(BaseListView):
    """
    API để admin liệt kê tất cả các chiến dịch khuyến mãi.
    GET /promotions/campaigns/admin
    
    Endpoint này chỉ dành cho admin, hiển thị tất cả các chiến dịch.
    """
    queryset = PromotionCampaign.objects.all()
    serializer_class = PromotionCampaignSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'start_date', 'end_date', 'created_at']
    ordering = ['-created_at']


class PromotionCampaignCreateView(BaseCreateView):
    """
    API để tạo mới chiến dịch khuyến mãi.
    POST /promotions/campaigns/admin
    
    Endpoint này chỉ dành cho admin.
    """
    queryset = PromotionCampaign.objects.all()
    serializer_class = PromotionCampaignSerializer
    permission_classes = [IsAdminUser]


class PromotionCampaignRetrieveView(BaseRetrieveView):
    """
    API để xem chi tiết một chiến dịch khuyến mãi.
    GET /promotions/campaigns/{id}
    
    Endpoint này dành cho admin.
    """
    queryset = PromotionCampaign.objects.all()
    serializer_class = PromotionCampaignSerializer
    permission_classes = [IsAdminUser]


class PromotionCampaignUpdateView(BaseUpdateView):
    """
    API để cập nhật một chiến dịch khuyến mãi.
    PUT/PATCH /promotions/campaigns/{id}
    
    Endpoint này chỉ dành cho admin.
    """
    queryset = PromotionCampaign.objects.all()
    serializer_class = PromotionCampaignSerializer
    permission_classes = [IsAdminUser]


class PromotionCampaignDestroyView(BaseDestroyView):
    """
    API để xóa một chiến dịch khuyến mãi.
    DELETE /promotions/campaigns/{id}
    
    Endpoint này chỉ dành cho admin.
    """
    queryset = PromotionCampaign.objects.all()
    serializer_class = PromotionCampaignSerializer
    permission_classes = [IsAdminUser]
