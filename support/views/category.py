"""
Support Category views module
"""
from rest_framework import generics
from rest_framework.permissions import AllowAny

from ..models import SupportCategory
from ..serializers import SupportCategorySerializer


class SupportCategoryListView(generics.ListAPIView):
    """
    API view để liệt kê tất cả các danh mục hỗ trợ đang hoạt động.
    
    GET /support/categories - Liệt kê danh mục hỗ trợ
    
    Bất kỳ ai cũng có thể truy cập.
    """
    queryset = SupportCategory.objects.filter(is_active=True)
    serializer_class = SupportCategorySerializer
    permission_classes = [AllowAny]
