from rest_framework import generics, status
from rest_framework.response import Response
from core.mixins.views import ApiResponseMixin, SerializerContextMixin


class BaseAPIView(ApiResponseMixin, SerializerContextMixin):
    """
    Base API View với các phương thức response chuẩn hóa
    và context serializer mở rộng.
    """
    pass


class BaseListView(BaseAPIView, generics.ListAPIView):
    """
    Base view cho các API endpoint GET - List (collection).
    """
    pass


class BaseCreateView(BaseAPIView, generics.CreateAPIView):
    """
    Base view cho các API endpoint POST - Create.
    """
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return self.success_response(
            data=serializer.data,
            message="Tạo mới thành công",
            status_code=status.HTTP_201_CREATED,
            headers=headers
        )


class BaseListCreateView(BaseAPIView, generics.ListCreateAPIView):
    """
    Base view cho các API endpoint GET/POST - List/Create.
    """
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return self.success_response(
            data=serializer.data,
            message="Tạo mới thành công",
            status_code=status.HTTP_201_CREATED,
            headers=headers
        )


class BaseRetrieveView(BaseAPIView, generics.RetrieveAPIView):
    """
    Base view cho các API endpoint GET - Detail.
    """
    pass


class BaseUpdateView(BaseAPIView, generics.UpdateAPIView):
    """
    Base view cho các API endpoint PUT/PATCH - Update.
    """
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # Nếu đã prefetch_related, reset lại để lấy dữ liệu mới nhất
            instance._prefetched_objects_cache = {}

        return self.success_response(
            data=serializer.data,
            message="Cập nhật thành công",
            status_code=status.HTTP_200_OK
        )


class BaseDestroyView(BaseAPIView, generics.DestroyAPIView):
    """
    Base view cho các API endpoint DELETE - Destroy.
    """
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return self.success_response(
            message="Xóa thành công",
            status_code=status.HTTP_204_NO_CONTENT
        )


class BaseRetrieveUpdateView(BaseAPIView, generics.RetrieveUpdateAPIView):
    """
    Base view cho các API endpoint GET/PUT/PATCH - Retrieve/Update.
    """
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return self.success_response(
            data=serializer.data,
            message="Cập nhật thành công",
            status_code=status.HTTP_200_OK
        )


class BaseRetrieveDestroyView(BaseAPIView, generics.RetrieveDestroyAPIView):
    """
    Base view cho các API endpoint GET/DELETE - Retrieve/Destroy.
    """
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return self.success_response(
            message="Xóa thành công",
            status_code=status.HTTP_204_NO_CONTENT
        )


class BaseRetrieveUpdateDestroyView(BaseAPIView, generics.RetrieveUpdateDestroyAPIView):
    """
    Base view cho các API endpoint GET/PUT/PATCH/DELETE - Retrieve/Update/Destroy.
    """
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return self.success_response(
            data=serializer.data,
            message="Cập nhật thành công",
            status_code=status.HTTP_200_OK
        )
        
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return self.success_response(
            message="Xóa thành công",
            status_code=status.HTTP_204_NO_CONTENT
        )
