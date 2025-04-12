from django.urls import path

from .views import PaymentCheckoutView, PaymentStatusView

app_name = 'payments'

urlpatterns = [
    # POST /checkout - thực hiện thanh toán
    path('/checkout', PaymentCheckoutView.as_view(), name='payment-checkout'),
    
    # GET /payments/{id}/status - kiểm tra trạng thái thanh toán
    path('/<int:pk>/status', PaymentStatusView.as_view(), name='payment-status'),
]
