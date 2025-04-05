"""
FAQ views module
"""
from rest_framework import generics
from rest_framework.permissions import AllowAny

from ..models import FAQ
from ..serializers import FAQSerializer


class FAQListView(generics.ListAPIView):
    """
    API view để liệt kê tất cả các FAQ đã xuất bản.
    
    GET /support/faqs - Liệt kê FAQ
    
    Bất kỳ ai cũng có thể truy cập.
    """
    serializer_class = FAQSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """
        Trả về các FAQ đã xuất bản, có thể lọc theo danh mục.
        """
        queryset = FAQ.objects.filter(is_published=True)
        category_id = self.request.query_params.get('category_id', None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset.order_by('order')
