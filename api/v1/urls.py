from django.urls import path, include

# Nhóm các URL theo module
urlpatterns = [
    # Authentication
    path('auth/', include(('user_auth.urls', 'user_auth'), namespace='auth_v1')),
    
    # Core modules
    path('products/', include(('products.urls', 'products'), namespace='products_v1')),
    path('users/', include(('users.urls', 'users'), namespace='users_v1')),
    path('customers/', include(('customers.urls', 'customers'), namespace='customers_v1')),
    path('cart/', include(('cart.urls', 'cart'), namespace='cart_v1')),
    path('orders/', include(('orders.urls', 'orders'), namespace='orders_v1')),
    
    # Additional modules
    path('catalog/', include(('catalog.urls', 'catalog'), namespace='catalog_v1')),
    path('hrm/', include(('hrm.urls', 'hrm'), namespace='hrm_v1')),
    path('reports/', include(('reports.urls', 'reports'), namespace='reports_v1')),
    
    # Optional modules (chỉ include nếu tồn tại)
    path('payments/', include(('payments.urls', 'payments'), namespace='payments_v1')),
    path('shipping/', include(('shipping.urls', 'shipping'), namespace='shipping_v1')),
    path('inventory/', include(('inventory.urls', 'inventory'), namespace='inventory_v1')),
    path('promotions/', include(('promotions.urls', 'promotions'), namespace='promotions_v1')),
    path('reviews/', include(('reviews.urls', 'reviews'), namespace='reviews_v1')),
    path('wishlist/', include(('wishlist.urls', 'wishlist'), namespace='wishlist_v1')),
    path('notifications/', include(('notifications.urls', 'notifications'), namespace='notifications_v1')),
    path('support/', include(('support.urls', 'support'), namespace='support_v1')),
    path('settings/', include(('settings.urls', 'settings'), namespace='settings_v1')),
    path('pages/', include(('pages.urls', 'pages'), namespace='pages_v1')),
]
