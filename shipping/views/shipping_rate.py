"""
Shipping Rate views module
"""
from rest_framework import filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from core.views.base import BaseListView, BaseCreateView, BaseRetrieveView, BaseUpdateView, BaseDestroyView
from ..models import ShippingRate, ShippingMethod, ShippingZone
from ..serializers import ShippingRateSerializer


class ShippingRateListView(BaseListView):
    """
    API để liệt kê tất cả các biểu phí vận chuyển.
    GET /shipping/rates
    """
    queryset = ShippingRate.objects.all()
    serializer_class = ShippingRateSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['shipping_method', 'shipping_zone', 'is_active', 'currency']
    ordering_fields = ['price', 'min_weight', 'max_weight', 'created_at']
    ordering = ['shipping_method', 'shipping_zone', 'min_weight']


class ShippingRateCreateView(BaseCreateView):
    """
    API để tạo mới biểu phí vận chuyển.
    POST /shipping/rates/create
    """
    queryset = ShippingRate.objects.all()
    serializer_class = ShippingRateSerializer
    permission_classes = [IsAdminUser]


class ShippingRateRetrieveView(BaseRetrieveView):
    """
    API để xem chi tiết một biểu phí vận chuyển.
    GET /shipping/rates/{id}
    """
    queryset = ShippingRate.objects.all()
    serializer_class = ShippingRateSerializer
    permission_classes = [IsAdminUser]


class ShippingRateUpdateView(BaseUpdateView):
    """
    API để cập nhật một biểu phí vận chuyển.
    PUT/PATCH /shipping/rates/{id}/update
    """
    queryset = ShippingRate.objects.all()
    serializer_class = ShippingRateSerializer
    permission_classes = [IsAdminUser]


class ShippingRateDestroyView(BaseDestroyView):
    """
    API để xóa một biểu phí vận chuyển.
    DELETE /shipping/rates/{id}/delete
    """
    queryset = ShippingRate.objects.all()
    serializer_class = ShippingRateSerializer
    permission_classes = [IsAdminUser]


class CalculateShippingRatesView(APIView):
    """
    API để tính toán các biểu phí vận chuyển khả dụng cho một đơn hàng.
    Yêu cầu order_id, shipping_address và total_weight.
    POST /shipping/calculate
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get('order_id')
        shipping_address = request.data.get('shipping_address')
        total_weight = request.data.get('total_weight')
        
        if not all([order_id, shipping_address, total_weight]):
            return Response(
                {"error": "order_id, shipping_address, and total_weight are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Chuyển đổi từ string sang float nếu cần
            if isinstance(total_weight, str):
                total_weight = float(total_weight)
                
            # Lấy thông tin địa chỉ
            country = shipping_address.get('country')
            province = shipping_address.get('province')
            
            if not country:
                return Response(
                    {"error": "Country is required in shipping address"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Tìm shipping zone phù hợp
            matching_zones = ShippingZone.objects.filter(
                is_active=True
            ).filter(
                Q(countries__icontains=country) | Q(countries='*')
            )
            
            if province:
                # Nếu có province, tìm zone phù hợp với province trước
                province_matching = matching_zones.filter(
                    Q(provinces__icontains=province) | Q(provinces='*')
                )
                if province_matching.exists():
                    matching_zones = province_matching
            
            if not matching_zones.exists():
                return Response(
                    {"error": "No shipping zones available for your location"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Lấy tất cả các shipping method đang hoạt động
            shipping_methods = ShippingMethod.objects.filter(is_active=True)
            
            if not shipping_methods.exists():
                return Response(
                    {"error": "No shipping methods available"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Tìm các shipping rate phù hợp
            available_rates = []
            
            for method in shipping_methods:
                for zone in matching_zones:
                    rates = ShippingRate.objects.filter(
                        shipping_method=method,
                        shipping_zone=zone,
                        is_active=True,
                        min_weight__lte=total_weight
                    ).filter(
                        Q(max_weight__isnull=True) | Q(max_weight__gte=total_weight)
                    )
                    
                    for rate in rates:
                        # Tính phí vận chuyển
                        shipping_fee = rate.price
                        if method.weight_multiplier:
                            shipping_fee += total_weight * method.weight_multiplier
                        
                        available_rates.append({
                            'rate_id': rate.id,
                            'method_id': method.id,
                            'method_name': method.name,
                            'price': shipping_fee,
                            'currency': rate.currency,
                            'estimated_days': method.estimated_days,
                            'description': method.description
                        })
            
            if not available_rates:
                return Response(
                    {"error": "No shipping rates available for your order weight and location"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Sắp xếp theo giá
            available_rates = sorted(available_rates, key=lambda x: x['price'])
            
            return Response({
                "available_rates": available_rates,
                "order_id": order_id,
                "total_weight": total_weight
            }, status=status.HTTP_200_OK)
            
        except ValueError:
            return Response(
                {"error": "Invalid weight value"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
