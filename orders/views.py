from cart.models import Cart, CartItem
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order, OrderItem
from .serializers import OrderSerializer


# API Tạo đơn hàng từ giỏ hàng
class CreateOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)

        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(user=request.user, status="pending")
        for item in cart_items:
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity,
                                     price=item.product.price)
        cart_items.delete()

        return Response({"message": "Order created successfully", "order_id": order.id}, status=status.HTTP_201_CREATED)


# API Lấy danh sách đơn hàng của user
class UserOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


# API Xem chi tiết đơn hàng
class OrderDetailView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


# API Cập nhật trạng thái đơn hàng (chỉ dành cho Seller/Admin)
class UpdateOrderStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, pk):
        try:
            order = Order.objects.get(id=pk)

            if not request.user.is_staff and order.items.filter(product__seller=request.user).count() == 0:
                return Response({"error": "You do not have permission to update this order"},
                                status=status.HTTP_403_FORBIDDEN)

            new_status = request.data.get("status")
            if new_status not in ["pending", "shipped", "delivered", "cancelled"]:
                return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

            order.status = new_status
            order.save()
            return Response({"message": "Order status updated successfully"}, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
