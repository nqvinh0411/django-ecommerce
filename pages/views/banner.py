"""
Banner views module
"""
from django.utils import timezone
from django.db.models import Q
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from core.mixins.swagger_helpers import SwaggerSchemaMixin

from ..models import Banner
from ..serializers import BannerSerializer
from ..permissions import IsAdminUserOrReadOnly


class BannerListCreateView(SwaggerSchemaMixin, generics.ListCreateAPIView):
    """
    API view để liệt kê tất cả các banner hoặc tạo một banner mới.
    
    GET /banners - Liệt kê banner
    POST /banners - Tạo banner mới
    
    Admin có thể tạo banner mới, trong khi bất kỳ ai cũng có thể xem banner đang hiển thị.
    Hỗ trợ lọc theo vị trí.
    """
    serializer_class = BannerSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['position', 'is_active']
    
    def get_queryset(self):
        """
        Trả về tất cả banner cho admin, nhưng chỉ trả về các banner đang hiển thị 
        và chưa hết hạn cho người dùng không phải admin.
        Query parameter tùy chọn cho vị trí.
        """
        queryset = Banner.objects.all()
        
        # Kiểm tra nếu đang trong quá trình tạo schema Swagger
        if getattr(self.request, 'swagger_fake_view', False) or self.is_swagger_generation:
            return queryset.none()
            
        # Non-admin users only see active and non-expired banners
        if not self.request.user.is_staff:
            now = timezone.now()
            queryset = queryset.filter(
                is_active=True
            ).filter(
                # Start time is null or in the past
                Q(start_time__isnull=True) | Q(start_time__lte=now)
            ).filter(
                # End time is null or in the future
                Q(end_time__isnull=True) | Q(end_time__gt=now)
            )
            
        return queryset
