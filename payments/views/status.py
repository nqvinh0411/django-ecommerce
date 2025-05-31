"""
Payment status views module
"""
from rest_framework import permissions

from core.views.base import BaseRetrieveView
from core.mixins.swagger_helpers import SwaggerSchemaMixin
from ..models import Payment
from ..serializers import PaymentStatusSerializer


class PaymentStatusView(SwaggerSchemaMixin, BaseRetrieveView):
    """
    API endpoint để xem trạng thái thanh toán (GET).
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentStatusSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Đảm bảo người dùng chỉ xem được các thanh toán của họ,
        trừ khi là admin.
        """
        queryset = super().get_queryset()
        
        # Kiểm tra nếu đang trong quá trình tạo schema Swagger
        if getattr(self.request, 'swagger_fake_view', False) or self.is_swagger_generation:
            return queryset.none()
            
        if not self.request.user.is_staff:
            queryset = queryset.filter(order__user=self.request.user)
        return queryset
