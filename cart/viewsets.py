"""
Cart API ViewSets.

Module này cung cấp các ViewSets chuẩn hóa cho Cart API,
tuân thủ định dạng response và quy ước API đã được thiết lập.
"""

from django.shortcuts import get_object_or_404
from products.models import Product
from rest_framework import permissions, status
from rest_framework.decorators import action

from core.viewsets.base import StandardizedModelViewSet
from core.permissions.base import IsOwner
from core.mixins.swagger_helpers import SwaggerSchemaMixin
from drf_spectacular.utils import extend_schema

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer, CartItemCreateSerializer


@extend_schema(tags=['Cart'])
class CartViewSet(SwaggerSchemaMixin, StandardizedModelViewSet):
    """
    ViewSet để quản lý Cart resources.
    
    Cung cấp các endpoints để xem và quản lý giỏ hàng của người dùng hiện tại.
    
    Endpoints:
    - GET /api/v1/cart/ - Xem thông tin giỏ hàng hiện tại
    - POST /api/v1/cart/items/ - Thêm sản phẩm vào giỏ hàng
    - PATCH /api/v1/cart/items/{id}/ - Cập nhật số lượng sản phẩm trong giỏ hàng
    - DELETE /api/v1/cart/items/{id}/ - Xóa sản phẩm khỏi giỏ hàng
    - DELETE /api/v1/cart/clear/ - Xóa tất cả sản phẩm trong giỏ hàng
    """
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Trả về queryset với chỉ giỏ hàng của người dùng hiện tại.
        """
        # Xử lý trường hợp đang tạo schema Swagger
        if self.is_swagger_generation:
            return Cart.objects.none()
            
        return Cart.objects.filter(user=self.request.user)
    
    def list(self, request, *args, **kwargs):
        """
        Xem thông tin giỏ hàng hiện tại.
        Nếu giỏ hàng chưa tồn tại, sẽ tạo mới.
        
        Returns:
            Response: Thông tin giỏ hàng
        """
        # Xử lý trường hợp đang tạo schema Swagger
        if self.is_swagger_generation:
            return self.success_response(data={})
            
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return self.success_response(
            data=serializer.data,
            message="Thông tin giỏ hàng",
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['post'], url_path='items')
    def add_item(self, request):
        """
        Thêm sản phẩm vào giỏ hàng.
        
        Args:
            request: HTTP request với product_id và quantity
            
        Returns:
            Response: Thông tin giỏ hàng sau khi thêm sản phẩm
        """
        serializer = CartItemCreateSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return self.error_response(
                errors=serializer.errors,
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
        cart_serializer = self.get_serializer(cart)
        return self.success_response(
            data=cart_serializer.data,
            message="Đã thêm sản phẩm vào giỏ hàng",
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['patch'], url_path='items/(?P<item_id>[^/.]+)')
    def update_item(self, request, item_id=None):
        """
        Cập nhật số lượng sản phẩm trong giỏ hàng.
        
        Args:
            request: HTTP request với quantity
            item_id: ID của cart item cần cập nhật
            
        Returns:
            Response: Thông tin giỏ hàng sau khi cập nhật
        """
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
            cart_serializer = self.get_serializer(cart)
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
    
    @action(detail=False, methods=['delete'], url_path='items/(?P<item_id>[^/.]+)')
    def delete_item(self, request, item_id=None):
        """
        Xóa sản phẩm khỏi giỏ hàng.
        
        Args:
            request: HTTP request
            item_id: ID của cart item cần xóa
            
        Returns:
            Response: Thông tin giỏ hàng sau khi xóa sản phẩm
        """
        try:
            # Lấy giỏ hàng của người dùng
            cart = Cart.objects.get(user=request.user)
            # Lấy item cần xóa
            cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
            
            # Xóa item
            cart_item.delete()
            
            # Trả về kết quả
            cart_serializer = self.get_serializer(cart)
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
    
    @action(detail=False, methods=['delete'], url_path='clear')
    def clear_cart(self, request):
        """
        Xóa tất cả sản phẩm trong giỏ hàng.
        
        Args:
            request: HTTP request
            
        Returns:
            Response: Thông báo xóa thành công
        """
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
