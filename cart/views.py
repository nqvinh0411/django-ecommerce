from products.models import Product
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart, CartItem
from .serializers import CartSerializer


# API Xem giỏ hàng
class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


# API Thêm sản phẩm vào giỏ hàng
class AddToCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        cart_item.quantity += quantity
        cart_item.save()

        return Response({"message": "Product added to cart successfully"}, status=200)


# API Cập nhật số lượng sản phẩm trong giỏ hàng
class UpdateCartItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))

        try:
            cart = Cart.objects.get(user=request.user)
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            cart_item.quantity = quantity
            cart_item.save()
            return Response({"message": "Cart updated successfully"}, status=200)
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response({"error": "Item not found in cart"}, status=404)


# API Xóa sản phẩm khỏi giỏ hàng
class RemoveFromCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        product_id = request.data.get("product_id")

        try:
            cart = Cart.objects.get(user=request.user)
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            cart_item.delete()
            return Response({"message": "Item removed from cart"}, status=200)
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response({"error": "Item not found in cart"}, status=404)
