from rest_framework.response import Response
from rest_framework import status


class ApiResponseMixin:
    """
    Mixin cung cấp các phương thức response chuẩn hóa.
    """
    
    @staticmethod
    def success_response(data=None, message="", status_code=status.HTTP_200_OK, headers=None, extra=None):
        """
        Tạo response thành công với cấu trúc chuẩn.
        """
        response_data = {
            "status": "success",
            "status_code": status_code,
            "message": message if message else "",
            "data": data if data else {}
        }
        
        # if message:
        #     response_data["message"] = message
        #
        # if data is not None:
        #     response_data["data"] = data

        if extra and isinstance(extra, dict):
            response_data.update(extra)
            
        return Response(response_data, status=status_code, headers=headers)
    
    @staticmethod
    def error_response(message="", errors=None, status_code=status.HTTP_400_BAD_REQUEST, headers=None, extra=None):
        """
        Tạo response lỗi với cấu trúc chuẩn.
        """
        response_data = {
            "status": "error",
            "status_code": status_code,
            "message": message or "Đã xảy ra lỗi"
        }
        
        if errors:
            response_data["errors"] = errors

        if extra and isinstance(extra, dict):
            response_data.update(extra)
            
        return Response(response_data, status=status_code, headers=headers)


class SerializerContextMixin:
    """
    Mixin cung cấp context cho serializer với request hiện tại.
    """
    
    def get_serializer_context(self):
        """
        Thêm request vào context serializer.
        """
        context = super().get_serializer_context()
        context.update({
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        })
        return context


class PermissionByActionMixin:
    """
    Mixin cho phép xác định permission_classes khác nhau cho các action khác nhau.
    """
    permission_classes_by_action = {}
    
    def get_permissions(self):
        """
        Lấy permission_classes dựa trên action hiện tại.
        Nếu không có permission_classes được xác định cho action,
        sử dụng permission_classes mặc định.
        """
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except (KeyError, AttributeError):
            return super().get_permissions()


class SerializerByActionMixin:
    """
    Mixin cho phép xác định serializer_class khác nhau cho các action khác nhau.
    """
    serializer_class_by_action = {}
    
    def get_serializer_class(self):
        """
        Lấy serializer_class dựa trên action hiện tại.
        Nếu không có serializer_class được xác định cho action,
        sử dụng serializer_class mặc định.
        """
        try:
            return self.serializer_class_by_action[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()
