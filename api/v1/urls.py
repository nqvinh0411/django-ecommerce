from django.urls import path, include

# Nhóm các URL theo module
urlpatterns = [
    # Module catalog
    path('', include('catalog.urls')),
    
    # Module wishlist
    path('', include('wishlist.urls')),
    
    # Module auth/users
    path('auth/', include('users.urls')),
    
    # Module customers
    path('', include('customers.urls')),
    
    # Module products
    path('', include('products.urls')),
    
    # Module inventory
    path('', include('inventory.urls')),
    
    # Module cart
    path('', include('cart.urls')),
    
    # Module orders
    path('', include('orders.urls')),
    
    # Module shipping
    path('', include('shipping.urls')),
    
    # Module payments
    path('', include('payments.urls')),
    
    # Module reviews
    path('', include('reviews.urls')),
    
    # Module promotions
    path('', include('promotions.urls')),
    
    # Module reports
    path('', include('reports.urls')),
]
