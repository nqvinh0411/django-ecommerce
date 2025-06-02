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
from .serializers import (
    CartSerializer, CartSummarySerializer, CartItemSerializer,
    CartItemCreateSerializer, CartItemUpdateSerializer, CartCheckoutSerializer
)


@extend_schema(tags=['Cart'])
class CartSelfViewSet(SwaggerSchemaMixin, StandardizedModelViewSet):
    """
    ViewSet để user quản lý Cart của chính mình.
    
    Cung cấp các endpoints để user xem và quản lý giỏ hàng của mình.
    
    Endpoints:
    - GET /api/v1/cart/me/ - Xem giỏ hàng hiện tại
    - POST /api/v1/cart/me/items/ - Thêm sản phẩm vào giỏ hàng
    - PUT/PATCH /api/v1/cart/me/items/{id}/ - Cập nhật số lượng sản phẩm
    - DELETE /api/v1/cart/me/items/{id}/ - Xóa sản phẩm khỏi giỏ hàng
    - DELETE /api/v1/cart/me/clear/ - Xóa tất cả sản phẩm
    - GET /api/v1/cart/me/summary/ - Tóm tắt giỏ hàng
    - POST /api/v1/cart/me/checkout/ - Checkout giỏ hàng
    """
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']
    
    def get_queryset(self):
        """Chỉ trả về cart của user hiện tại."""
        if self.is_swagger_generation:
            return Cart.objects.none()
        return Cart.objects.filter(user=self.request.user)
    
    def get_cart(self):
        """Get or create cart for current user."""
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart
    
    def list(self, request, *args, **kwargs):
        """
        Xem thông tin giỏ hàng hiện tại.
        Nếu giỏ hàng chưa tồn tại, sẽ tạo mới.
        """
        cart = self.get_cart()
        serializer = self.get_serializer(cart)
        return self.success_response(
            data=serializer.data,
            message="Thông tin giỏ hàng",
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Lấy tóm tắt giỏ hàng (không bao gồm chi tiết items).
        """
        cart = self.get_cart()
        serializer = CartSummarySerializer(cart)
        return self.success_response(
            data=serializer.data,
            message="Tóm tắt giỏ hàng",
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['post'], url_path='items')
    def add_item(self, request):
        """
        Thêm sản phẩm vào giỏ hàng.
        
        Body:
            - product_id: ID của sản phẩm
            - quantity: Số lượng (mặc định: 1)
        """
        serializer = CartItemCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        cart = self.get_cart()
        product_id = serializer.validated_data.get('product_id')
        quantity = serializer.validated_data.get('quantity', 1)
        
        # Get product
        product = get_object_or_404(Product, id=product_id)
        
        # Add item to cart using model method
        cart_item = cart.add_item(product, quantity)
        
        # Return updated cart
        cart_serializer = self.get_serializer(cart)
        return self.success_response(
            data=cart_serializer.data,
            message="Đã thêm sản phẩm vào giỏ hàng",
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['put', 'patch'], url_path='items/(?P<item_id>[^/.]+)')
    def update_item(self, request, item_id=None):
        """
        Cập nhật số lượng sản phẩm trong giỏ hàng.
        
        Args:
            item_id: ID của cart item
            
        Body:
            - quantity: Số lượng mới
        """
        cart = self.get_cart()
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        
        serializer = CartItemUpdateSerializer(cart_item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Return updated cart
        cart_serializer = self.get_serializer(cart)
        return self.success_response(
            data=cart_serializer.data,
            message="Đã cập nhật giỏ hàng",
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['delete'], url_path='items/(?P<item_id>[^/.]+)')
    def remove_item(self, request, item_id=None):
        """
        Xóa sản phẩm khỏi giỏ hàng.
        
        Args:
            item_id: ID của cart item cần xóa
        """
        cart = self.get_cart()
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        
        cart_item.delete()
        
        # Return updated cart
        cart_serializer = self.get_serializer(cart)
        return self.success_response(
            data=cart_serializer.data,
            message="Đã xóa sản phẩm khỏi giỏ hàng",
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """
        Xóa tất cả sản phẩm trong giỏ hàng.
        """
        cart = self.get_cart()
        cart.clear()
        
        # Return empty cart
        cart_serializer = self.get_serializer(cart)
        return self.success_response(
            data=cart_serializer.data,
            message="Đã xóa tất cả sản phẩm trong giỏ hàng",
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['post'])
    def checkout(self, request):
        """
        Checkout giỏ hàng - chuyển sang tạo đơn hàng.
        
        Body:
            - shipping_address: Địa chỉ giao hàng (bắt buộc)
            - billing_address: Địa chỉ thanh toán (tùy chọn)
            - notes: Ghi chú (tùy chọn)
        """
        cart = self.get_cart()
        
        if cart.is_empty:
            return self.error_response(
                message="Giỏ hàng đang trống",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CartCheckoutSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        # Prepare checkout data
        checkout_data = {
            'cart': cart,
            'user': request.user,
            'total_amount': cart.total_amount,
            'total_items': cart.total_items,
            **serializer.validated_data
        }
        
        return self.success_response(
            data=checkout_data,
            message="Sẵn sàng checkout. Vui lòng chuyển sang tạo đơn hàng.",
            status_code=status.HTTP_200_OK
        )


@extend_schema(tags=['Cart Management'])
class CartItemAdminViewSet(SwaggerSchemaMixin, StandardizedModelViewSet):
    """
    ViewSet để admin quản lý tất cả CartItem resources.
    
    Hỗ trợ tất cả các operations CRUD cho CartItem với định dạng response
    chuẩn hóa và phân quyền admin.
    
    Endpoints:
    - GET /api/v1/cart/admin/items/ - Liệt kê tất cả cart items (admin only)
    - GET /api/v1/cart/admin/items/{id}/ - Xem chi tiết cart item (admin only)
    - PUT/PATCH /api/v1/cart/admin/items/{id}/ - Cập nhật cart item (admin only)
    - DELETE /api/v1/cart/admin/items/{id}/ - Xóa cart item (admin only)
    """
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAdminUser]
    filterset_fields = ['cart__user', 'product', 'created_at']
    search_fields = ['cart__user__email', 'product__name']
    ordering_fields = ['created_at', 'updated_at', 'quantity']
    ordering = ['-created_at']


@extend_schema(tags=['Cart Management'])  
class CartAdminViewSet(SwaggerSchemaMixin, StandardizedModelViewSet):
    """
    ViewSet để admin quản lý tất cả Cart resources.
    
    Hỗ trợ tất cả các operations cho Cart với định dạng response
    chuẩn hóa và phân quyền admin.
    
    Endpoints:
    - GET /api/v1/cart/admin/ - Liệt kê tất cả carts (admin only)
    - GET /api/v1/cart/admin/{id}/ - Xem chi tiết cart (admin only)
    - DELETE /api/v1/cart/admin/{id}/ - Xóa cart (admin only)
    """
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAdminUser]
    filterset_fields = ['user', 'created_at', 'updated_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']
    http_method_names = ['get', 'delete', 'head', 'options']  # No create/update for admin
    
    def get_serializer_class(self):
        """Use summary serializer for list view"""
        if self.action == 'list':
            return CartSummarySerializer
        return CartSerializer
