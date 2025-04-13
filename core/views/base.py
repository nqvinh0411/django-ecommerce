# core/views/base.py

from rest_framework import generics, status
from rest_framework.response import Response
from core.mixins.views import ApiResponseMixin, SerializerContextMixin


class BaseAPIView(ApiResponseMixin, SerializerContextMixin, generics.GenericAPIView):
    """
    Base API View chuẩn hóa sẵn create, update, destroy.
    """

    def create(self, request, *args, **kwargs):
        """
        API endpoint để tạo mới một đối tượng.
        """
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


    def update(self, request, *args, **kwargs):
        # partial = kwargs.pop('partial', False)
        partial = True
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


# Các BaseView theo chức năng riêng biệt, kế thừa BaseAPIView

class BaseListView(BaseAPIView, generics.ListAPIView):
    """Base view cho GET - List (collection)."""
    pass

class BaseCreateView(BaseAPIView, generics.CreateAPIView):
    """Base view cho POST - Create."""
    pass

class BaseListCreateView(BaseAPIView, generics.ListCreateAPIView):
    """Base view cho GET/POST - List + Create."""
    pass

class BaseRetrieveView(BaseAPIView, generics.RetrieveAPIView):
    """Base view cho GET - Retrieve (Detail)."""
    pass

class BaseUpdateView(BaseAPIView, generics.UpdateAPIView):
    """Base view cho PUT/PATCH - Update."""
    pass

class BaseDestroyView(BaseAPIView, generics.DestroyAPIView):
    """Base view cho DELETE - Destroy."""
    pass

class BaseRetrieveUpdateView(BaseAPIView, generics.RetrieveUpdateAPIView):
    """Base view cho GET/PUT/PATCH - Retrieve + Update."""
    pass

class BaseRetrieveDestroyView(BaseAPIView, generics.RetrieveDestroyAPIView):
    """Base view cho GET/DELETE - Retrieve + Destroy."""
    pass

class BaseRetrieveUpdateDestroyView(BaseAPIView, generics.RetrieveUpdateDestroyAPIView):
    """Base view cho GET/PUT/PATCH/DELETE - Retrieve + Update + Destroy."""
    pass
