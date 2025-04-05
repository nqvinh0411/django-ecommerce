"""
Language settings views module
"""
from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from ..models import LanguageSetting
from ..serializers import LanguageSettingSerializer


class LanguageSettingListView(generics.ListAPIView):
    """
    API view để liệt kê tất cả các cài đặt ngôn ngữ.
    
    GET /settings/languages - Liệt kê cài đặt ngôn ngữ
    
    Chỉ admin mới có thể truy cập.
    """
    queryset = LanguageSetting.objects.all()
    serializer_class = LanguageSettingSerializer
    permission_classes = [IsAdminUser]
