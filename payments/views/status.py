"""
Payment status views module
"""
from rest_framework import permissions

from core.views.base import BaseRetrieveView
from ..models import Payment
from ..serializers import PaymentStatusSerializer


class PaymentStatusView(BaseRetrieveView):
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
        if not self.request.user.is_staff:
            queryset = queryset.filter(order__user=self.request.user)
        return queryset
