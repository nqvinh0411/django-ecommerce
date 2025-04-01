from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from customers.models import Customer
from .models import Wishlist, WishlistItem
from .serializers import WishlistSerializer, WishlistItemSerializer
from .permissions import IsWishlistOwner


class WishlistView(APIView):
    """
    View to get the current user's wishlist.
    Automatically creates a wishlist if the user doesn't have one.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Get or create customer's wishlist
        customer = get_object_or_404(Customer, user=request.user)
        wishlist, created = Wishlist.objects.get_or_create(customer=customer)
        
        serializer = WishlistSerializer(wishlist)
        return Response(serializer.data)


class AddWishlistItemView(APIView):
    """
    View to add a product to the user's wishlist.
    Automatically creates a wishlist if the user doesn't have one.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Get required data
        product_id = request.data.get('product_id')
        if not product_id:
            return Response(
                {'error': 'product_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Get or create customer's wishlist
        customer = get_object_or_404(Customer, user=request.user)
        wishlist, created = Wishlist.objects.get_or_create(customer=customer)
        
        # Create serializer with the data
        serializer = WishlistItemSerializer(data={'product_id': product_id})
        
        if serializer.is_valid():
            # Check if item already exists
            if WishlistItem.objects.filter(wishlist=wishlist, product_id=product_id).exists():
                return Response(
                    {'message': 'This product is already in your wishlist'},
                    status=status.HTTP_200_OK
                )
                
            # Save the item
            serializer.save(wishlist=wishlist)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RemoveWishlistItemView(APIView):
    """
    View to remove a product from the user's wishlist.
    """
    permission_classes = [IsAuthenticated, IsWishlistOwner]
    
    def delete(self, request, item_id):
        # Get the item
        item = get_object_or_404(WishlistItem, id=item_id)
        
        # Check permissions
        self.check_object_permissions(request, item)
        
        # Delete the item
        item.delete()
        
        return Response(
            {'message': 'Item removed from wishlist successfully'},
            status=status.HTTP_204_NO_CONTENT
        )
