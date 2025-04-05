"""
Email template views module
"""
from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from ..models import EmailTemplate
from ..serializers import EmailTemplateSerializer


class EmailTemplateListCreateView(generics.ListCreateAPIView):
    """
    API view để liệt kê tất cả các mẫu email hoặc tạo mẫu mới.
    
    GET /settings/emails - Liệt kê mẫu email
    POST /settings/emails - Tạo mẫu email mới
    
    Chỉ admin mới có thể truy cập.
    """
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [IsAdminUser]


class EmailTemplateRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view để xem, cập nhật hoặc xóa một mẫu email.
    
    GET /settings/emails/{id} - Xem chi tiết mẫu email
    PUT/PATCH /settings/emails/{id} - Cập nhật mẫu email
    DELETE /settings/emails/{id} - Xóa mẫu email
    
    Chỉ admin mới có thể truy cập.
    """
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [IsAdminUser]
