from rest_framework.permissions import BasePermission


class IsWishlistOwner(BasePermission):
    """
    Custom permission to only allow owners of a wishlist to access it.
    """
    message = "You do not have permission to access this wishlist."

    def has_object_permission(self, request, view, obj):
        # Check if the user is the owner of the wishlist
        if hasattr(obj, 'wishlist'):
            # For WishlistItem objects
            return obj.wishlist.customer.user == request.user
        else:
            # For Wishlist objects
            return obj.customer.user == request.user
