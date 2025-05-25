"""
Settings API ViewSets.

Module này cung cấp các ViewSets chuẩn hóa cho Settings API,
tuân thủ định dạng response và quy ước API đã được thiết lập.
"""

from rest_framework import permissions, status, filters
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from core.viewsets.base import StandardizedModelViewSet
from core.permissions.base import IsAdminOrReadOnly
from core.optimization.decorators import log_slow_queries
from core.optimization.mixins import QueryOptimizationMixin

from .models import StoreSetting, Currency, LanguageSetting, EmailTemplate
from .serializers import (
    StoreSettingSerializer, CurrencySerializer, 
    LanguageSettingSerializer, EmailTemplateSerializer
)
from .permissions import CanManageSettings


class StoreSettingViewSet(QueryOptimizationMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý StoreSetting resources.
    
    Cung cấp các operations xem và cập nhật cài đặt cửa hàng với định dạng response
    chuẩn hóa và phân quyền phù hợp. Chỉ quản trị viên mới có quyền thay đổi cài đặt.
    
    Endpoints:
    - GET /api/v1/settings/store/ - Lấy danh sách tất cả cài đặt cửa hàng
    - GET /api/v1/settings/store/{id}/ - Xem chi tiết một cài đặt cửa hàng
    - POST /api/v1/settings/store/ - Tạo mới cài đặt cửa hàng
    - PUT /api/v1/settings/store/{id}/ - Cập nhật toàn bộ cài đặt cửa hàng
    - PATCH /api/v1/settings/store/{id}/ - Cập nhật một phần cài đặt cửa hàng
    - DELETE /api/v1/settings/store/{id}/ - Xóa cài đặt cửa hàng
    - POST /api/v1/settings/store/toggle-maintenance/ - Bật/tắt chế độ bảo trì
    
    Permissions:
    - CanManageSettings: Chỉ người dùng có quyền quản lý cài đặt mới có thể thực hiện các thao tác
    
    Parameters:
    - id (int): ID của cài đặt cửa hàng
    - maintenance_mode (bool): Trạng thái chế độ bảo trì (chỉ dùng cho toggle-maintenance action)
    
    Returns:
    - 200 OK: Thành công, trả về dữ liệu cài đặt cửa hàng
    - 201 Created: Tạo mới cài đặt thành công
    - 400 Bad Request: Dữ liệu không hợp lệ
    - 401 Unauthorized: Không có quyền truy cập
    - 403 Forbidden: Không đủ quyền để thực hiện hành động
    - 404 Not Found: Không tìm thấy cài đặt cửa hàng
    """
    queryset = StoreSetting.objects.all()
    serializer_class = StoreSettingSerializer
    permission_classes = [CanManageSettings]
    
    select_related_fields = ['default_currency', 'default_language']
    
    def get_object(self):
        """
        Luôn trả về instance duy nhất của StoreSetting.
        """
        return StoreSetting.get_settings()
    
    def list(self, request, *args, **kwargs):
        """
        Ghi đè list để luôn trả về instance duy nhất.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.success_response(
            data=serializer.data,
            message="Cài đặt cửa hàng",
            status_code=status.HTTP_200_OK
        )
    
    def create(self, request, *args, **kwargs):
        """
        Ghi đè create để chuyển hướng đến update nếu instance đã tồn tại.
        """
        return self.update(request, *args, **kwargs)
    
    @action(detail=False, methods=['post'])
    def toggle_maintenance(self, request):
        """
        Bật/tắt chế độ bảo trì.
        """
        store_setting = self.get_object()
        store_setting.is_maintenance_mode = not store_setting.is_maintenance_mode
        store_setting.save()
        
        mode_status = "bật" if store_setting.is_maintenance_mode else "tắt"
        
        serializer = self.get_serializer(store_setting)
        return self.success_response(
            data=serializer.data,
            message=f"Đã {mode_status} chế độ bảo trì",
            status_code=status.HTTP_200_OK
        )


class CurrencyViewSet(QueryOptimizationMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý Currency resources.
    
    Cung cấp các operations CRUD cho tiền tệ với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/settings/currencies/ - Liệt kê tất cả tiền tệ
    - POST /api/v1/settings/currencies/ - Tạo tiền tệ mới
    - GET /api/v1/settings/currencies/{id}/ - Xem chi tiết tiền tệ
    - PUT/PATCH /api/v1/settings/currencies/{id}/ - Cập nhật tiền tệ
    - DELETE /api/v1/settings/currencies/{id}/ - Xóa tiền tệ
    - POST /api/v1/settings/currencies/{id}/set-as-default/ - Đặt làm tiền tệ mặc định
    """
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code', 'name']
    filterset_fields = ['is_active', 'is_default']
    ordering_fields = ['code', 'name', 'exchange_rate_to_base']
    ordering = ['-is_default', 'code']
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def set_as_default(self, request, pk=None):
        """
        Đặt tiền tệ làm mặc định.
        """
        currency = self.get_object()
        
        if currency.is_default:
            return self.error_response(
                message="Tiền tệ này đã là mặc định",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        currency.is_default = True
        currency.save()
        
        serializer = self.get_serializer(currency)
        return self.success_response(
            data=serializer.data,
            message=f"Đã đặt {currency.code} làm tiền tệ mặc định",
            status_code=status.HTTP_200_OK
        )


class LanguageSettingViewSet(QueryOptimizationMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý LanguageSetting resources.
    
    Cung cấp các operations CRUD cho ngôn ngữ với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/settings/languages/ - Liệt kê tất cả ngôn ngữ
    - POST /api/v1/settings/languages/ - Tạo ngôn ngữ mới
    - GET /api/v1/settings/languages/{id}/ - Xem chi tiết ngôn ngữ
    - PUT/PATCH /api/v1/settings/languages/{id}/ - Cập nhật ngôn ngữ
    - DELETE /api/v1/settings/languages/{id}/ - Xóa ngôn ngữ
    - POST /api/v1/settings/languages/{id}/set-as-default/ - Đặt làm ngôn ngữ mặc định
    """
    queryset = LanguageSetting.objects.all()
    serializer_class = LanguageSettingSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code', 'name']
    filterset_fields = ['is_active', 'is_default']
    ordering_fields = ['code', 'name']
    ordering = ['-is_default', 'code']
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def set_as_default(self, request, pk=None):
        """
        Đặt ngôn ngữ làm mặc định.
        """
        language = self.get_object()
        
        if language.is_default:
            return self.error_response(
                message="Ngôn ngữ này đã là mặc định",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        language.is_default = True
        language.save()
        
        serializer = self.get_serializer(language)
        return self.success_response(
            data=serializer.data,
            message=f"Đã đặt {language.name} làm ngôn ngữ mặc định",
            status_code=status.HTTP_200_OK
        )


class EmailTemplateViewSet(QueryOptimizationMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý EmailTemplate resources.
    
    Cung cấp các operations CRUD cho mẫu email với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/settings/email-templates/ - Liệt kê tất cả mẫu email
    - POST /api/v1/settings/email-templates/ - Tạo mẫu email mới
    - GET /api/v1/settings/email-templates/{id}/ - Xem chi tiết mẫu email
    - PUT/PATCH /api/v1/settings/email-templates/{id}/ - Cập nhật mẫu email
    - DELETE /api/v1/settings/email-templates/{id}/ - Xóa mẫu email
    - GET /api/v1/settings/email-templates/by-key/{template_key}/ - Lấy mẫu email theo khóa
    - POST /api/v1/settings/email-templates/{id}/preview/ - Xem trước mẫu email
    """
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [CanManageSettings]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['template_key', 'subject', 'description']
    filterset_fields = ['is_active']
    ordering_fields = ['template_key', 'subject', 'updated_at']
    ordering = ['template_key']
    
    @action(detail=False, methods=['get'], url_path='by-key/(?P<template_key>[^/.]+)')
    @log_slow_queries(threshold_ms=500)
    def by_key(self, request, template_key=None):
        """
        Lấy mẫu email theo khóa.
        """
        try:
            template = EmailTemplate.objects.get(template_key=template_key)
            serializer = self.get_serializer(template)
            return self.success_response(
                data=serializer.data,
                message=f"Mẫu email {template_key}",
                status_code=status.HTTP_200_OK
            )
        except EmailTemplate.DoesNotExist:
            return self.error_response(
                message=f"Không tìm thấy mẫu email với khóa {template_key}",
                status_code=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def preview(self, request, pk=None):
        """
        Xem trước mẫu email với dữ liệu mẫu.
        """
        template = self.get_object()
        
        # Lấy dữ liệu mẫu từ request hoặc sử dụng dữ liệu mặc định
        sample_data = request.data.get('sample_data', {
            'user': {
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john.doe@example.com'
            },
            'order': {
                'order_number': 'ORD-12345',
                'total': '100.00',
                'date': '2025-05-25'
            },
            'store': {
                'name': StoreSetting.get_settings().store_name,
                'support_email': StoreSetting.get_settings().support_email
            }
        })
        
        try:
            rendered_html = template.render_html(sample_data)
            rendered_text = template.render_text(sample_data)
            
            return self.success_response(
                data={
                    'subject': template.render_subject(sample_data),
                    'html_content': rendered_html,
                    'text_content': rendered_text
                },
                message=f"Xem trước mẫu email {template.template_key}",
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return self.error_response(
                message=f"Lỗi khi render mẫu email: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
