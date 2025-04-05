"""
Store settings views module
"""
from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from ..models import StoreSetting
from ..serializers import StoreSettingSerializer


class StoreSettingView(generics.RetrieveUpdateAPIView):
    """
    API view để xem hoặc cập nhật cài đặt cửa hàng.
    
    GET /settings/store - Xem cài đặt cửa hàng
    PUT/PATCH /settings/store - Cập nhật cài đặt cửa hàng
    
    Chỉ tồn tại một instance và chỉ admin mới có thể truy cập.
    """
    serializer_class = StoreSettingSerializer
    permission_classes = [IsAdminUser]
    
    def get_object(self):
        """
        Lấy hoặc tạo instance cài đặt cửa hàng.
        """
        return StoreSetting.get_settings()
