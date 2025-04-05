"""
Payment checkout views module
"""
import uuid
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order
from ..models import Payment


class PaymentCheckoutView(APIView):
    """
    API endpoint để thực hiện thanh toán (POST).
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        order_id = request.data.get("order_id")

        try:
            order = Order.objects.get(id=order_id, user=request.user)
            if Payment.objects.filter(order=order).exists():
                return Response({"error": "Order is already paid"}, status=status.HTTP_400_BAD_REQUEST)

            # Giả lập xử lý thanh toán (thực tế có thể tích hợp với cổng thanh toán như Stripe, VNPay)
            transaction_id = str(uuid.uuid4())  # Tạo mã giao dịch ngẫu nhiên
            payment = Payment.objects.create(
                order=order,
                transaction_id=transaction_id,
                amount=sum(item.price * item.quantity for item in order.items.all()),
                status="completed"  # Giả lập thanh toán thành công
            )

            return Response(
                {"message": "Payment successful", "transaction_id": transaction_id},
                status=status.HTTP_201_CREATED
            )
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
