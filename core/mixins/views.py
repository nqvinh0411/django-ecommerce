from rest_framework.response import Response
from rest_framework import status
# from django.utils.decorators import method_decorator
# from django.views.decorators.csrf import csrf_exempt
#
#
# class CsrfExemptMixin:
#     @method_decorator(csrf_exempt)
#     def dispatch(self, request, *args, **kwargs):
#         return super().dispatch(request, *args, **kwargs)


class FilterByTenantMixin:
    """
    Mixin để lọc dữ liệu theo tenant (người thuê) hiện tại.
    
    Trong hệ thống multi-tenant, mixin này đảm bảo rằng mỗi tenant 
    chỉ có thể xem và quản lý dữ liệu của chính họ.
    
    Sử dụng:
    1. Thêm mixin này vào ViewSet
    2. Mỗi model cần có trường tenant hoặc một cách để liên kết đến tenant
    
    Lưu ý: ViewSet sử dụng mixin này cần override lại phương thức get_queryset()
    để triển khai logic lọc cụ thể cho model đó.
    """
    def get_tenant(self):
        """
        Trả về tenant hiện tại dựa trên người dùng đang đăng nhập.
        
        Override phương thức này để xác định tenant theo logic ứng dụng.
        Mặc định, tenant được xem là user hiện tại.
        """
        return self.request.user if hasattr(self, 'request') else None
    
    def filter_by_tenant(self, queryset):
        """
        Lọc queryset theo tenant hiện tại.
        
        Đây là phương thức cơ bản, các lớp con nên override lại phương thức
        get_queryset() để triển khai logic lọc cụ thể.
        """
        tenant = self.get_tenant()
        if tenant is None or tenant.is_staff:
            return queryset  # Admin thấy tất cả
        
        # Mặc định giả định model có trường 'tenant'
        # Nếu không, cần override lại phương thức này
        filter_kwargs = {'tenant': tenant}
        return queryset.filter(**filter_kwargs)
    
    def get_queryset(self):
        """
        Trả về queryset đã được lọc theo tenant hiện tại.
        """
        queryset = super().get_queryset()
        return self.filter_by_tenant(queryset)


class ApiResponseMixin:
    """
    Mixin cung cấp các phương thức response chuẩn hóa cho API views.
    
    Mixin này định nghĩa các phương thức để tạo response thành công và lỗi 
    với một định dạng nhất quán trên toàn bộ hệ thống e-commerce.
    Kết quả trả về sẽ tuân theo định dạng chuẩn:
    
    Đối với thành công:
    {
        "status": "success",
        "status_code": xxx,
        "message": "Thông báo thành công (nếu có)",
        "data": { ... } 
    }
    
    Đối với lỗi:
    {
        "status": "error",
        "status_code": xxx,
        "message": "Thông báo lỗi",
        "errors": { ... } // Chi tiết lỗi (nếu có)
    }
    """
    
    @staticmethod
    def success_response(data=None, message="", status_code=status.HTTP_200_OK, headers=None, extra=None):
        """
        Tạo response thành công với cấu trúc chuẩn.
        
        Args:
            data (dict, optional): Dữ liệu trả về cho client. Mặc định: None.
            message (str, optional): Thông báo thành công. Mặc định: "".
            status_code (int, optional): HTTP status code. Mặc định: 200.
            headers (dict, optional): HTTP headers bổ sung. Mặc định: None.
            extra (dict, optional): Dữ liệu bổ sung sẽ được gộp vào response. Mặc định: None.
            
        Returns:
            Response: DRF Response object với dữ liệu đã được định dạng chuẩn.
            
        Example:
            return self.success_response(
                data={'user': user_data},
                message="Đăng nhập thành công",
                status_code=status.HTTP_200_OK
            )
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
        
        Args:
            message (str, optional): Thông báo lỗi tổng quát. Mặc định: "Đã xảy ra lỗi" nếu không cung cấp.
            errors (dict, optional): Chi tiết lỗi, thường là validation errors theo field. Mặc định: None.
            status_code (int, optional): HTTP status code. Mặc định: 400.
            headers (dict, optional): HTTP headers bổ sung. Mặc định: None.
            extra (dict, optional): Dữ liệu bổ sung sẽ được gộp vào response. Mặc định: None.
            
        Returns:
            Response: DRF Response object với thông tin lỗi đã được định dạng chuẩn.
            
        Example:
            return self.error_response(
                message="Không thể xác thực người dùng",
                errors={"email": ["Email không tồn tại"]},
                status_code=status.HTTP_401_UNAUTHORIZED
            )
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
    
    Mixin này tự động thêm một số thông tin hữu ích vào serializer context,
    giúp serializer có thể truy cập các dữ liệu như request, format và view
    trong quá trình serialization/deserialization.
    
    Điều này đặc biệt hữu ích khi cần kiểm tra quyền truy cập, 
    tạo URL tuyệt đối, hoặc truy cập thông tin người dùng hiện tại.
    
    Note:
        Mixin này giả định rằng lớp cha đã có phương thức `get_serializer_context()`.
        Thường thì nó được kế thừa cùng với GenericAPIView.
    """
    
    def get_serializer_context(self):
        """
        Thêm request và các thông tin khác vào context của serializer.
        
        Phương thức này mở rộng context mặc định bằng cách thêm reference đến:
        - request: HTTP request hiện tại
        - format: format được yêu cầu (vd: 'json', 'api')
        - view: reference đến view hiện tại
        
        Returns:
            dict: Context đã được mở rộng cho serializer.
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
    
    Khi sử dụng ViewSets, các action khác nhau (list, create, retrieve, update, etc.)
    thường yêu cầu các permissions khác nhau. Mixin này cho phép định nghĩa các
    permission classes cụ thể cho từng action.
    
    Attributes:
        permission_classes_by_action (dict): Dictionary ánh xạ tên action 
            đến danh sách các permission classes sẽ được áp dụng.
            
    Example:
        ```python
        class ProductViewSet(PermissionByActionMixin, ModelViewSet):
            permission_classes = [IsAuthenticated]  # Mặc định cho tất cả actions
            permission_classes_by_action = {
                'list': [AllowAny],  # Cho phép tất cả user xem danh sách
                'create': [IsAdminUser],  # Chỉ admin mới có thể tạo mới
                'update': [IsAdminOrOwner],  # Admin hoặc chủ sở hữu mới được cập nhật
                'destroy': [IsAdminUser]  # Chỉ admin mới có thể xóa
            }
        ```
    """
    permission_classes_by_action = {}
    
    def get_permissions(self):
        """
        Lấy permission_classes dựa trên action hiện tại.
        
        Phương thức này kiểm tra xem action hiện tại có trong 
        `permission_classes_by_action` không và trả về permissions tương ứng.
        Nếu không tìm thấy action, sẽ sử dụng permission_classes mặc định.
        
        Returns:
            list: Danh sách các permission objects đã được khởi tạo.
            
        Note:
            Action thường được xác định tự động bởi DRF cho các ViewSets,
            tương ứng với các phương thức HTTP:
            - 'list': GET trên collection
            - 'create': POST trên collection
            - 'retrieve': GET trên item
            - 'update': PUT trên item
            - 'partial_update': PATCH trên item
            - 'destroy': DELETE trên item
        """
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except (KeyError, AttributeError):
            return super().get_permissions()


class SerializerByActionMixin:
    """
    Mixin cho phép xác định serializer_class khác nhau cho các action khác nhau.
    
    Tương tự như PermissionByActionMixin, mixin này giúp sử dụng các serializers
    khác nhau tùy thuộc vào action đang được thực hiện. Điều này đặc biệt hữu ích
    khi cần hiển thị các trường khác nhau cho các thao tác khác nhau (ví dụ: hiển thị 
    thông tin rút gọn khi liệt kê nhưng chi tiết khi xem một item).
    
    Attributes:
        serializer_class_by_action (dict): Dictionary ánh xạ tên action
            đến serializer class sẽ được sử dụng.
            
    Example:
        ```python
        class ProductViewSet(SerializerByActionMixin, ModelViewSet):
            serializer_class = ProductSerializer  # Serializer mặc định
            serializer_class_by_action = {
                'list': ProductListSerializer,  # Serializer rút gọn cho danh sách
                'create': ProductCreateSerializer,  # Serializer cho tạo mới
                'update': ProductUpdateSerializer,  # Serializer cho cập nhật
            }
        ```
    """
    serializer_class_by_action = {}
    
    def get_serializer_class(self):
        """
        Lấy serializer_class dựa trên action hiện tại.
        
        Phương thức này kiểm tra xem action hiện tại có trong 
        `serializer_class_by_action` không và trả về serializer class tương ứng.
        Nếu không tìm thấy action, sẽ sử dụng serializer_class mặc định.
        
        Returns:
            class: Serializer class sẽ được sử dụng.
            
        Note:
            Việc sử dụng serializers khác nhau giúp tối ưu hóa lượng dữ liệu được
            truyền tải và tránh việc hiển thị dữ liệu không cần thiết hoặc nhạy cảm.
        """
        try:
            return self.serializer_class_by_action[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()
