"""
URL configuration for e_commerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # API routes - Versioned API structure
    path('api/', include('api.urls')),
    
    # Legacy routes - Kept for backwards compatibility during transition
    # These should eventually be migrated to the versioned API structure
    path('api/auth/', include('users.urls', namespace='users')),
    path('api/products/', include('products.urls', namespace='products')),
    path('api/cart/', include('cart.urls', namespace='carts')),
    path('api/orders/', include('orders.urls', namespace='orders')),
    path('api/payments/', include('payments.urls', namespace='payments')),
    path('api/reviews/', include('reviews.urls', namespace='reviews')),
    path('api/notifications/', include('notifications.urls', namespace='notifications')),
    path('api/catalog/', include('catalog.urls', namespace='catalog')),
    path('api/customer/', include('customers.urls', namespace='customer')),
    path('api/inventory/', include('inventory.urls', namespace='inventory')),
    path('api/shipping/', include('shipping.urls', namespace='shipping')),
    path('api/promotions/', include('promotions.urls', namespace='promotions')),
    path('api/wishlist/', include('wishlist.urls', namespace='wishlist')),
    path('api/reports/', include('reports.urls', namespace='reports')),
    path('api/settings/', include('settings.urls', namespace='settings')),
    path('api/pages/', include('pages.urls', namespace='pages')),
    path('api/support/', include('support.urls', namespace='support')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
