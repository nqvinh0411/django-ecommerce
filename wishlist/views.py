from rest_framework.generics import (
    RetrieveAPIView, CreateAPIView, DestroyAPIView, 
    ListAPIView, GenericAPIView
)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from customers.models import Customer
from .models import Wishlist, WishlistItem
from .serializers import WishlistSerializer, WishlistItemSerializer
from .permissions import IsWishlistOwner


class WishlistRetrieveView(RetrieveAPIView):
    """
    Retrieve the current user's wishlist.
    
    GET /wishlist - Returns the wishlist details with all items
    
    Automatically creates a wishlist if the user doesn't have one.
    """
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        customer = get_object_or_404(Customer, user=self.request.user)
        wishlist, created = Wishlist.objects.get_or_create(customer=customer)
        return wishlist


class WishlistItemListView(ListAPIView):
    """
    List all items in the user's wishlist.
    
    GET /wishlist/items - Returns a list of all wishlist items
    """
    serializer_class = WishlistItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        customer = get_object_or_404(Customer, user=self.request.user)
        wishlist, created = Wishlist.objects.get_or_create(customer=customer)
        return WishlistItem.objects.filter(wishlist=wishlist)


class WishlistItemCreateView(CreateAPIView):
    """
    Add a product to the user's wishlist.
    
    POST /wishlist/items
    
    Request body:
    {
        "product_id": <int>
    }
    """
    serializer_class = WishlistItemSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        # Get or create customer's wishlist
        customer = get_object_or_404(Customer, user=self.request.user)
        wishlist, created = Wishlist.objects.get_or_create(customer=customer)
        
        # Check if item already exists
        product = serializer.validated_data['product']
        if WishlistItem.objects.filter(wishlist=wishlist, product=product).exists():
            from rest_framework.serializers import ValidationError
            raise ValidationError(
                {"product_id": "This product is already in your wishlist"}
            )
        
        # Save the item
        serializer.save(wishlist=wishlist)


class WishlistItemRetrieveView(RetrieveAPIView):
    """
    Retrieve a specific wishlist item.
    
    GET /wishlist/items/{id} - Returns details of a specific wishlist item
    """
    serializer_class = WishlistItemSerializer
    permission_classes = [IsAuthenticated, IsWishlistOwner]
    lookup_url_kwarg = 'item_id'
    
    def get_queryset(self):
        customer = get_object_or_404(Customer, user=self.request.user)
        wishlist = get_object_or_404(Wishlist, customer=customer)
        return WishlistItem.objects.filter(wishlist=wishlist)


class WishlistItemDestroyView(DestroyAPIView):
    """
    Remove a product from the user's wishlist.
    
    DELETE /wishlist/items/{id} - Removes an item from the wishlist
    """
    serializer_class = WishlistItemSerializer
    permission_classes = [IsAuthenticated, IsWishlistOwner]
    lookup_url_kwarg = 'item_id'
    
    def get_queryset(self):
        customer = get_object_or_404(Customer, user=self.request.user)
        wishlist = get_object_or_404(Wishlist, customer=customer)
        return WishlistItem.objects.filter(wishlist=wishlist)
