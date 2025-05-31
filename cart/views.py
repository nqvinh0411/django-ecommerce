from django.shortcuts import get_object_or_404
from products.models import Product
from rest_framework import permissions, status

from core.views.base import BaseAPIView
from core.permissions.base import IsOwner

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer, CartItemCreateSerializer


class CartDetailView(BaseAPIView):
    """
    API để xem thông tin giỏ hàng hiện tại của người dùng.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartSerializer

    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return self.success_response(
            data=serializer.data,
            message="Thông tin giỏ hàng",
            status_code=status.HTTP_200_OK
        )


class CartItemCreateView(BaseAPIView):
    """
    API để thêm sản phẩm vào giỏ hàng.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartItemCreateSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return self.error_response(
                data=serializer.errors,
                message="Dữ liệu không hợp lệ",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        # Lấy hoặc tạo giỏ hàng
        cart, created = Cart.objects.get_or_create(user=request.user)
        product_id = serializer.validated_data.get('product_id')
        quantity = serializer.validated_data.get('quantity', 1)
        
        # Kiểm tra sản phẩm
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return self.error_response(
                message="Không tìm thấy sản phẩm",
                status_code=status.HTTP_404_NOT_FOUND
            )
            
        # Thêm sản phẩm vào giỏ hàng hoặc cập nhật số lượng
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if created:
            cart_item.quantity = quantity
        else:
            cart_item.quantity += quantity
        cart_item.save()
        
        # Trả về kết quả
        cart_serializer = CartSerializer(cart)
        return self.success_response(
            data=cart_serializer.data,
            message="Đã thêm sản phẩm vào giỏ hàng",
            status_code=status.HTTP_200_OK
        )


class CartItemUpdateView(BaseAPIView):
    """
    API để cập nhật số lượng sản phẩm trong giỏ hàng.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartSerializer  # Sử dụng CartSerializer vì nó được trả về trong response
    
    def patch(self, request, item_id):
        try:
            # Lấy giỏ hàng của người dùng
            cart = Cart.objects.get(user=request.user)
            # Lấy item cần cập nhật
            cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
            
            # Cập nhật số lượng
            quantity = request.data.get('quantity')
            if not quantity or int(quantity) < 1:
                return self.error_response(
                    message="Số lượng không hợp lệ",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
                
            cart_item.quantity = int(quantity)
            cart_item.save()
            
            # Trả về kết quả
            cart_serializer = CartSerializer(cart)
            return self.success_response(
                data=cart_serializer.data,
                message="Đã cập nhật giỏ hàng",
                status_code=status.HTTP_200_OK
            )
        except Cart.DoesNotExist:
            return self.error_response(
                message="Không tìm thấy giỏ hàng",
                status_code=status.HTTP_404_NOT_FOUND
            )


class CartItemDeleteView(BaseAPIView):
    """
    API để xóa sản phẩm khỏi giỏ hàng.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartSerializer  # Sử dụng CartSerializer vì nó được trả về trong response
    
    def delete(self, request, item_id):
        try:
            # Lấy giỏ hàng của người dùng
            cart = Cart.objects.get(user=request.user)
            # Lấy item cần xóa
            cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
            
            # Xóa item
            cart_item.delete()
            
            # Trả về kết quả
            cart_serializer = CartSerializer(cart)
            return self.success_response(
                data=cart_serializer.data,
                message="Đã xóa sản phẩm khỏi giỏ hàng",
                status_code=status.HTTP_200_OK
            )
        except Cart.DoesNotExist:
            return self.error_response(
                message="Không tìm thấy giỏ hàng",
                status_code=status.HTTP_404_NOT_FOUND
            )


class CartClearView(BaseAPIView):
    """
    API để xóa tất cả sản phẩm trong giỏ hàng.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartSerializer  # Sử dụng CartSerializer cho schema generation
    
    def delete(self, request):
        try:
            # Lấy giỏ hàng của người dùng
            cart = Cart.objects.get(user=request.user)
            # Xóa tất cả items
            CartItem.objects.filter(cart=cart).delete()
            
            # Trả về kết quả
            return self.success_response(
                message="Đã xóa tất cả sản phẩm trong giỏ hàng",
                status_code=status.HTTP_200_OK
            )
        except Cart.DoesNotExist:
            return self.error_response(
                message="Không tìm thấy giỏ hàng",
                status_code=status.HTTP_404_NOT_FOUND
            )
