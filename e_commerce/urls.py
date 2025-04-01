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
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls', namespace='users')),
    path('api/products/', include('products.urls', namespace='products')),
    path('api/cart/', include('cart.urls', namespace='carts')),
    path('api/orders/', include('orders.urls', namespace='orders')),
    path('api/payments/', include('payments.urls', namespace='payments')),
    path('api/reviews/', include('reviews.urls', namespace='reviews')),
    path('api/notifications/', include('notifications.urls')),
    path('api/catalog/', include('catalog.urls')),
    path('api/inventory/', include('inventory.urls')),
    path('api/shipping/', include('shipping.urls')),
    path('api/promotions/', include('promotions.urls')),
    path('api/wishlist/', include('wishlist.urls')),
    path('api/reports/', include('reports.urls')),
    path('api/settings/', include('settings.urls')),
    path('api/pages/', include('pages.urls')),
    path('api/support/', include('support.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
