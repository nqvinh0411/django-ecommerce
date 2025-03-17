from django.urls import path

from .views import PaymentCheckoutView, PaymentStatusView

urlpatterns = [
    path('checkout/', PaymentCheckoutView.as_view(), name='payment-checkout'),
    path('<int:pk>/status/', PaymentStatusView.as_view(), name='payment-status'),
]
