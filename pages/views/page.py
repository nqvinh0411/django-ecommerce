"""
Page views module
"""
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from core.mixins.swagger_helpers import SwaggerSchemaMixin

from ..models import Page
from ..serializers import PageSerializer
from ..permissions import IsAdminUserOrReadOnly


class PageListCreateView(SwaggerSchemaMixin, generics.ListCreateAPIView):
    """
    API view để liệt kê tất cả các trang hoặc tạo một trang mới.
    
    GET /pages - Liệt kê trang
    POST /pages - Tạo trang mới
    
    Admin có thể tạo trang mới, trong khi bất kỳ ai cũng có thể xem các trang đã xuất bản.
    """
    serializer_class = PageSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_published']
    search_fields = ['title', 'slug', 'content_text']
    
    def get_queryset(self):
        """
        Trả về tất cả các trang cho admin, nhưng chỉ trả về các trang đã xuất bản 
        cho người dùng không phải admin.
        """
        queryset = Page.objects.all()
        
        # Non-admin users only see published pages
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                is_published=True,
                published_at__lte=timezone.now()
            )
            
        return queryset


class PageRetrieveUpdateDestroyBySlugView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view để xem, cập nhật hoặc xóa một trang theo slug.
    
    GET /pages/{slug} - Xem chi tiết trang
    PUT/PATCH /pages/{slug} - Cập nhật trang
    DELETE /pages/{slug} - Xóa trang
    
    Admin có thể cập nhật/xóa, trong khi bất kỳ ai cũng có thể xem các trang đã xuất bản.
    """
    serializer_class = PageSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    lookup_field = 'slug'
    
    def get_queryset(self):
        """
        Trả về tất cả các trang cho admin, nhưng chỉ trả về các trang đã xuất bản 
        cho người dùng không phải admin.
        """
        queryset = Page.objects.all()
        
        # Non-admin users only see published pages
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                is_published=True,
                published_at__lte=timezone.now()
            )
            
        return queryset
