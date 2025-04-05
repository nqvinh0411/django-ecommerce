"""
Currency views module
"""
from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from ..models import Currency
from ..serializers import CurrencySerializer


class CurrencyListView(generics.ListAPIView):
    """
    API view để liệt kê tất cả các loại tiền tệ.
    
    GET /settings/currencies - Liệt kê các loại tiền tệ
    
    Chỉ admin mới có thể truy cập.
    """
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [IsAdminUser]
