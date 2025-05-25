"""
Base ViewSets.

Module này cung cấp các lớp ViewSet cơ sở chuẩn hóa để các API
khác trong hệ thống có thể kế thừa, đảm bảo nhất quán trong
định dạng response và xử lý lỗi.
"""

from rest_framework import viewsets, status, mixins
from rest_framework.response import Response

from core.utils.response import success_response, error_response, paginated_response
from core.mixins.views import ApiResponseMixin, SerializerContextMixin, PermissionByActionMixin


class StandardizedViewSet(ApiResponseMixin, SerializerContextMixin, PermissionByActionMixin, viewsets.ViewSet):
    """
    Lớp ViewSet cơ sở chuẩn hóa cho tất cả các ViewSets trong hệ thống.
    
    ViewSet này tích hợp các mixins chuẩn hóa đảm bảo tất cả API
    responses tuân theo định dạng đã định nghĩa.
    """
    
    def get_serializer_class(self):
        """
        Lấy serializer class phù hợp với action hiện tại.
        
        Override phương thức này trong các lớp con để xác định
        serializer class khác nhau cho các actions khác nhau.
        
        Returns:
            Serializer class
        """
        return self.serializer_class


class StandardizedModelViewSet(StandardizedViewSet, viewsets.ModelViewSet):
    """
    ModelViewSet chuẩn hóa cho CRUD operations.
    
    ViewSet này tích hợp đầy đủ các chức năng CRUD với định dạng
    response chuẩn hóa.
    """
    
    def list(self, request, *args, **kwargs):
        """
        List resources với response phân trang chuẩn hóa.
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_data = self.get_paginated_response(serializer.data)
            return self.success_response(
                data=paginated_data.data,
                status_code=status.HTTP_200_OK
            )
            
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    def create(self, request, *args, **kwargs):
        """
        Create resource với response chuẩn hóa.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return self.success_response(
            data=serializer.data,
            message="Resource created successfully",
            status_code=status.HTTP_201_CREATED
        )
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve resource với response chuẩn hóa.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return self.success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    def update(self, request, *args, **kwargs):
        """
        Update resource với response chuẩn hóa.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return self.success_response(
            data=serializer.data,
            message="Resource updated successfully",
            status_code=status.HTTP_200_OK
        )
    
    def partial_update(self, request, *args, **kwargs):
        """
        Partial update resource với response chuẩn hóa.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return self.success_response(
            data=serializer.data,
            message="Resource partially updated successfully",
            status_code=status.HTTP_200_OK
        )
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete resource với response chuẩn hóa.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        
        return self.success_response(
            message="Resource deleted successfully",
            status_code=status.HTTP_204_NO_CONTENT
        )


class ReadOnlyStandardizedModelViewSet(StandardizedViewSet, viewsets.ReadOnlyModelViewSet):
    """
    ModelViewSet chuẩn hóa chỉ đọc.
    
    ViewSet này chỉ hỗ trợ các operations list và retrieve với
    định dạng response chuẩn hóa.
    """
    
    def list(self, request, *args, **kwargs):
        """
        List resources với response phân trang chuẩn hóa.
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_data = self.get_paginated_response(serializer.data)
            return self.success_response(
                data=paginated_data.data,
                status_code=status.HTTP_200_OK
            )
            
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve resource với response chuẩn hóa.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return self.success_response(
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
