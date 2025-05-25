"""
Wishlist API ViewSets.

Module này cung cấp các ViewSets chuẩn hóa cho Wishlist API,
tuân thủ định dạng response và quy ước API đã được thiết lập.
"""

from rest_framework import permissions, status
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from core.viewsets.base import StandardizedModelViewSet
from customers.models import Customer
from products.models import Product
from .models import Wishlist, WishlistItem
from .serializers import WishlistSerializer, WishlistItemSerializer
from .permissions import IsWishlistOwner


class WishlistViewSet(StandardizedModelViewSet):
    """
    ViewSet để quản lý Wishlist resources.
    
    Cung cấp các endpoints để xem và quản lý danh sách sản phẩm yêu thích của người dùng.
    
    Endpoints:
    - GET /api/v1/wishlist/ - Xem danh sách yêu thích của người dùng
    - GET /api/v1/wishlist/items/ - Liệt kê tất cả các sản phẩm trong danh sách yêu thích
    - POST /api/v1/wishlist/items/ - Thêm sản phẩm vào danh sách yêu thích
    - GET /api/v1/wishlist/items/{id}/ - Xem chi tiết một sản phẩm trong danh sách yêu thích
    - DELETE /api/v1/wishlist/items/{id}/ - Xóa sản phẩm khỏi danh sách yêu thích
    - DELETE /api/v1/wishlist/clear/ - Xóa tất cả sản phẩm khỏi danh sách yêu thích
    """
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    
    def get_queryset(self):
        """
        Lấy wishlist của người dùng hiện tại.
        """
        customer = get_object_or_404(Customer, user=self.request.user)
        return Wishlist.objects.filter(customer=customer)
    
    def list(self, request, *args, **kwargs):
        """
        Trả về danh sách yêu thích của người dùng hiện tại.
        Tự động tạo danh sách nếu người dùng chưa có.
        """
        customer = get_object_or_404(Customer, user=request.user)
        wishlist, created = Wishlist.objects.get_or_create(customer=customer)
        serializer = self.get_serializer(wishlist)
        
        return self.success_response(
            data=serializer.data,
            message="Danh sách yêu thích của bạn",
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'], url_path='items')
    def items(self, request):
        """
        Lấy danh sách các sản phẩm trong wishlist của người dùng.
        """
        customer = get_object_or_404(Customer, user=request.user)
        wishlist, created = Wishlist.objects.get_or_create(customer=customer)
        wishlist_items = WishlistItem.objects.filter(wishlist=wishlist)
        
        serializer = WishlistItemSerializer(wishlist_items, many=True)
        return self.success_response(
            data=serializer.data,
            message="Danh sách sản phẩm yêu thích",
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['post'], url_path='items')
    def add_item(self, request):
        """
        Thêm một sản phẩm vào wishlist.
        """
        customer = get_object_or_404(Customer, user=request.user)
        wishlist, created = Wishlist.objects.get_or_create(customer=customer)
        
        serializer = WishlistItemSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.validated_data['product']
            
            # Kiểm tra xem sản phẩm đã có trong wishlist chưa
            if WishlistItem.objects.filter(wishlist=wishlist, product=product).exists():
                return self.error_response(
                    message="Sản phẩm này đã có trong danh sách yêu thích của bạn",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            wishlist_item = serializer.save(wishlist=wishlist)
            return self.success_response(
                data=serializer.data,
                message="Đã thêm sản phẩm vào danh sách yêu thích",
                status_code=status.HTTP_201_CREATED
            )
        
        return self.error_response(
            errors=serializer.errors,
            message="Dữ liệu không hợp lệ",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['post'], url_path='items/bulk-add')
    def bulk_add_items(self, request):
        """
        Thêm nhiều sản phẩm vào wishlist cùng lúc.
        """
        customer = get_object_or_404(Customer, user=request.user)
        wishlist, created = Wishlist.objects.get_or_create(customer=customer)
        
        product_ids = request.data.get('product_ids', [])
        if not product_ids:
            return self.error_response(
                message="Vui lòng cung cấp danh sách ID sản phẩm",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        added_items = []
        existing_items = []
        not_found_items = []
        
        for product_id in product_ids:
            try:
                product = Product.objects.get(id=product_id)
                
                # Kiểm tra xem sản phẩm đã có trong wishlist chưa
                if WishlistItem.objects.filter(wishlist=wishlist, product=product).exists():
                    existing_items.append(product_id)
                    continue
                
                # Thêm sản phẩm vào wishlist
                item = WishlistItem.objects.create(wishlist=wishlist, product=product)
                added_items.append(product_id)
                
            except Product.DoesNotExist:
                not_found_items.append(product_id)
        
        response_data = {
            'added_items': added_items,
            'existing_items': existing_items,
            'not_found_items': not_found_items
        }
        
        return self.success_response(
            data=response_data,
            message="Đã xử lý yêu cầu thêm sản phẩm vào danh sách yêu thích",
            status_code=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get', 'delete'], url_path='items/(?P<item_id>[^/.]+)')
    def item_detail(self, request, pk=None, item_id=None):
        """
        Xem chi tiết hoặc xóa một sản phẩm cụ thể trong wishlist.
        """
        customer = get_object_or_404(Customer, user=request.user)
        wishlist = get_object_or_404(Wishlist, customer=customer)
        
        try:
            item = WishlistItem.objects.get(id=item_id, wishlist=wishlist)
        except WishlistItem.DoesNotExist:
            return self.error_response(
                message="Không tìm thấy sản phẩm trong danh sách yêu thích",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        if request.method == 'GET':
            serializer = WishlistItemSerializer(item)
            return self.success_response(
                data=serializer.data,
                message="Chi tiết sản phẩm yêu thích",
                status_code=status.HTTP_200_OK
            )
        
        # DELETE
        item.delete()
        return self.success_response(
            data=None,
            message="Đã xóa sản phẩm khỏi danh sách yêu thích",
            status_code=status.HTTP_204_NO_CONTENT
        )
    
    @action(detail=False, methods=['delete'], url_path='clear')
    def clear(self, request):
        """
        Xóa tất cả sản phẩm khỏi wishlist.
        """
        customer = get_object_or_404(Customer, user=request.user)
        wishlist, created = Wishlist.objects.get_or_create(customer=customer)
        
        items_count = WishlistItem.objects.filter(wishlist=wishlist).count()
        WishlistItem.objects.filter(wishlist=wishlist).delete()
        
        return self.success_response(
            data={'removed_count': items_count},
            message="Đã xóa tất cả sản phẩm khỏi danh sách yêu thích",
            status_code=status.HTTP_200_OK
        )
