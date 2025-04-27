# core/views/base.py

from rest_framework import generics, status
from rest_framework.response import Response
from core.mixins.views import ApiResponseMixin, SerializerContextMixin


class BaseAPIView(ApiResponseMixin, SerializerContextMixin, generics.GenericAPIView):
    """
    Base API View chuẩn hóa sẵn các phương thức cơ bản trong toàn bộ hệ thống e-commerce.
    
    Class này kết hợp các mixins từ core.mixins với GenericAPIView từ DRF, 
    tạo thành lớp cơ sở cho tất cả API views trong hệ thống. BaseAPIView cung cấp:
    
    1. Các phương thức response chuẩn hóa (từ ApiResponseMixin)
    2. Context mở rộng cho serializers (từ SerializerContextMixin)
    3. Phương thức create, update, destroy với response chuẩn hóa
    
    Tất cả các API view trong hệ thống nên kế thừa từ BaseAPIView hoặc
    các specialized views được định nghĩa ở cuối file này (BaseListView, 
    BaseCreateView, etc.) thay vì sử dụng trực tiếp các views từ DRF.
    
    Attributes:
        permission_classes: List các permission classes sẽ áp dụng
        serializer_class: Class serializer chính
        queryset: QuerySet mặc định cho view
    """

    def create(self, request, *args, **kwargs):
        """
        Tạo mới một đối tượng thông qua API.
        
        Phương thức này thực hiện quá trình tạo mới một đối tượng, bao gồm:
        1. Deserialize và validate dữ liệu từ request
        2. Tạo đối tượng mới trong database
        3. Trả về response chuẩn hóa với dữ liệu đã tạo
        
        Args:
            request (Request): DRF Request object
            *args: Arguments bổ sung
            **kwargs: Keyword arguments bổ sung
            
        Returns:
            Response: Response chuẩn với status=201 và dữ liệu đối tượng đã tạo
            
        Raises:
            ValidationError: Nếu dữ liệu không hợp lệ
            
        Note:
            Kế thừa từ GenericAPIView.create nhưng sử dụng success_response
            thay vì trả về Response trực tiếp để đảm bảo format chuẩn.
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

    def perform_create(self, serializer):
        """
        Thực hiện việc lưu đối tượng mới.
        
        Hook này cho phép tùy chỉnh quá trình lưu, ví dụ để thêm
        các trường bổ sung từ request hoặc thiết lập mối quan hệ.
        
        Args:
            serializer (Serializer): DRF Serializer instance đã validate
            
        Returns:
            None
        """
        serializer.save()

    def update(self, request, *args, **kwargs):
        """
        Cập nhật một đối tượng hiện có.
        
        Mặc định, update luôn là partial update (PATCH) thay vì PUT,
        cho phép cập nhật một phần đối tượng thay vì thay thế hoàn toàn.
        
        Args:
            request (Request): DRF Request object
            *args: Arguments bổ sung
            **kwargs: Keyword arguments bổ sung
            
        Returns:
            Response: Response chuẩn với status=200 và dữ liệu đã cập nhật
            
        Raises:
            ValidationError: Nếu dữ liệu không hợp lệ
            NotFound: Nếu đối tượng không tồn tại
            
        Note:
            Khác với DRF, partial=True là mặc định, đơn giản hóa API
            và giảm nguy cơ mất dữ liệu.
        """
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

    def perform_update(self, serializer):
        """
        Thực hiện việc lưu đối tượng đã cập nhật.
        
        Hook này cho phép tùy chỉnh quá trình cập nhật, như thêm
        metadata hoặc xử lý logic bổ sung trước khi lưu.
        
        Args:
            serializer (Serializer): DRF Serializer instance đã validate
            
        Returns:
            None
        """
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        """
        Xóa một đối tượng hiện có.
        
        Args:
            request (Request): DRF Request object
            *args: Arguments bổ sung
            **kwargs: Keyword arguments bổ sung
            
        Returns:
            Response: Response chuẩn với status=204 và không có dữ liệu
            
        Raises:
            NotFound: Nếu đối tượng không tồn tại
            PermissionDenied: Nếu người dùng không có quyền xóa
            
        Note:
            Mặc dù status là 204 (No Content), response vẫn có message
            thành công để duy trì tính nhất quán của API.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return self.success_response(
            message="Xóa thành công",
            status_code=status.HTTP_204_NO_CONTENT
        )

    def perform_destroy(self, instance):
        """
        Thực hiện việc xóa đối tượng.
        
        Hook này cho phép tùy chỉnh quá trình xóa, ví dụ để thực hiện
        soft delete thay vì xóa thật từ database.
        
        Args:
            instance: Đối tượng cần xóa
            
        Returns:
            None
        """
        instance.delete()


# Các BaseView theo chức năng riêng biệt, kế thừa BaseAPIView

class BaseListView(BaseAPIView, generics.ListAPIView):
    """
    Base view cho việc liệt kê danh sách các đối tượng (GET - List).
    
    View này kết hợp BaseAPIView (cho response chuẩn hóa) và ListAPIView từ DRF
    để cung cấp một endpoint chỉ đọc liệt kê danh sách các đối tượng.
    
    Attributes:
        pagination_class: Class phân trang, mặc định lấy từ settings
        filter_backends: Các filter backends cho phép lọc, sắp xếp
        ordering: Thứ tự sắp xếp mặc định
        
    Example:
        ```python
        class ProductListView(BaseListView):
            queryset = Product.objects.filter(is_active=True)
            serializer_class = ProductSerializer
            permission_classes = [AllowAny]
            filter_backends = [DjangoFilterBackend, SearchFilter]
            filterset_fields = ['category', 'brand']
            search_fields = ['name', 'description']
            ordering = ['-created_at']
        ```
    """
    pass

class BaseCreateView(BaseAPIView, generics.CreateAPIView):
    """
    Base view cho việc tạo mới đối tượng (POST - Create).
    
    View này kết hợp BaseAPIView và CreateAPIView từ DRF để cung cấp
    một endpoint tạo mới đối tượng với response chuẩn hóa.
    
    Attributes:
        serializer_class: Serializer dùng để validate và lưu dữ liệu
        
    Example:
        ```python
        class ProductCreateView(BaseCreateView):
            serializer_class = ProductCreateSerializer
            permission_classes = [IsAuthenticated, IsAdminUser]
            
            def perform_create(self, serializer):
                # Tùy chỉnh logic tạo
                serializer.save(created_by=self.request.user)
        ```
    """
    pass

class BaseListCreateView(BaseAPIView, generics.ListCreateAPIView):
    """
    Base view kết hợp liệt kê và tạo mới (GET/POST - List + Create).
    
    View này cung cấp hai chức năng trong một endpoint:
    - GET: Liệt kê danh sách đối tượng (như BaseListView)
    - POST: Tạo mới đối tượng (như BaseCreateView)
    
    Thích hợp cho RESTful API nơi endpoint collection ('/products')
    được sử dụng cho cả việc liệt kê và tạo mới.
    
    Example:
        ```python
        class ProductListCreateView(BaseListCreateView):
            queryset = Product.objects.all()
            serializer_class = ProductSerializer
            permission_classes = [IsAuthenticatedOrReadOnly]
            
            # Tùy chỉnh serializer theo action
            def get_serializer_class(self):
                if self.request.method == 'POST':
                    return ProductCreateSerializer
                return ProductSerializer
        ```
    """
    pass

class BaseRetrieveView(BaseAPIView, generics.RetrieveAPIView):
    """
    Base view cho việc xem chi tiết một đối tượng (GET - Retrieve).
    
    View này cung cấp endpoint để lấy chi tiết của một đối tượng đơn lẻ
    dựa trên ID hoặc lookup field khác.
    
    Attributes:
        lookup_field: Trường dùng để tìm kiếm đối tượng (mặc định: 'pk')
        lookup_url_kwarg: Tên tham số trong URL (mặc định: giống lookup_field)
        
    Example:
        ```python
        class ProductDetailView(BaseRetrieveView):
            queryset = Product.objects.all()
            serializer_class = ProductDetailSerializer
            lookup_field = 'slug'  # Sử dụng slug thay vì ID
        ```
    """
    pass

class BaseUpdateView(BaseAPIView, generics.UpdateAPIView):
    """
    Base view cho việc cập nhật đối tượng (PUT/PATCH - Update).
    
    View này cung cấp endpoint để cập nhật một đối tượng hiện có.
    Mặc định, view này hỗ trợ cả PUT (thay thế hoàn toàn) và 
    PATCH (cập nhật một phần), nhưng luôn xử lý như partial update
    để tránh mất dữ liệu.
    
    Example:
        ```python
        class ProductUpdateView(BaseUpdateView):
            queryset = Product.objects.all()
            serializer_class = ProductUpdateSerializer
            permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
            
            def perform_update(self, serializer):
                serializer.save(updated_by=self.request.user)
        ```
    """
    pass

class BaseDestroyView(BaseAPIView, generics.DestroyAPIView):
    """
    Base view cho việc xóa đối tượng (DELETE - Destroy).
    
    View này cung cấp endpoint để xóa một đối tượng hiện có.
    
    Lưu ý:
        Thông thường, nên cần cân nhắc soft delete thay vì xóa thật,
        đặc biệt đối với các đối tượng có liên kết hoặc lịch sử giao dịch.
        
    Example:
        ```python
        class ProductDeleteView(BaseDestroyView):
            queryset = Product.objects.all()
            permission_classes = [IsAuthenticated, IsAdminUser]
            
            def perform_destroy(self, instance):
                # Soft delete thay vì xóa thật
                instance.is_active = False
                instance.deleted_at = timezone.now()
                instance.save()
        ```
    """
    pass

class BaseRetrieveUpdateView(BaseAPIView, generics.RetrieveUpdateAPIView):
    """
    Base view kết hợp xem chi tiết và cập nhật (GET/PUT/PATCH).
    
    View này cung cấp các chức năng trong một endpoint:
    - GET: Xem chi tiết đối tượng (như BaseRetrieveView)
    - PUT/PATCH: Cập nhật đối tượng (như BaseUpdateView)
    
    Thích hợp cho RESTful API nơi endpoint item ('/products/123')
    được sử dụng cho cả việc xem và cập nhật.
    
    Example:
        ```python
        class ProductDetailUpdateView(BaseRetrieveUpdateView):
            queryset = Product.objects.all()
            serializer_class = ProductSerializer
            permission_classes = [IsAuthenticatedOrReadOnly]
            
            def get_permissions(self):
                if self.request.method in ['PUT', 'PATCH']:
                    return [IsAuthenticated(), IsOwnerOrAdmin()]
                return [AllowAny()]
        ```
    """
    pass

class BaseRetrieveDestroyView(BaseAPIView, generics.RetrieveDestroyAPIView):
    """
    Base view kết hợp xem chi tiết và xóa (GET/DELETE).
    
    View này cung cấp các chức năng trong một endpoint:
    - GET: Xem chi tiết đối tượng (như BaseRetrieveView)
    - DELETE: Xóa đối tượng (như BaseDestroyView)
    
    Thích hợp khi bạn muốn hiển thị đối tượng và cho phép xóa,
    nhưng không cần chức năng cập nhật.
    
    Example:
        ```python
        class CommentViewDetail(BaseRetrieveDestroyView):
            queryset = Comment.objects.all()
            serializer_class = CommentSerializer
            
            def get_permissions(self):
                if self.request.method == 'DELETE':
                    return [IsAuthenticated(), IsOwnerOrAdmin()]
                return [AllowAny()]
        ```
    """
    pass

class BaseRetrieveUpdateDestroyView(BaseAPIView, generics.RetrieveUpdateDestroyAPIView):
    """
    Base view đầy đủ cho xem chi tiết, cập nhật và xóa (GET/PUT/PATCH/DELETE).
    
    View này cung cấp đầy đủ các chức năng CRUD (trừ Create) trong một endpoint:
    - GET: Xem chi tiết đối tượng
    - PUT/PATCH: Cập nhật đối tượng
    - DELETE: Xóa đối tượng
    
    Đây là view phổ biến nhất cho endpoints item trong RESTful API
    tiêu chuẩn, tuân theo các quy tắc HTTP method.
    
    Example:
        ```python
        class ProductDetailView(BaseRetrieveUpdateDestroyView):
            queryset = Product.objects.all()
            serializer_class = ProductSerializer
            permission_classes = [IsAuthenticated]
            
            def get_permissions(self):
                if self.request.method == 'GET':
                    return [AllowAny()]
                elif self.request.method in ['PUT', 'PATCH']:
                    return [IsAuthenticated(), IsOwnerOrAdmin()]
                else:  # DELETE
                    return [IsAuthenticated(), IsAdminUser()]
        ```
    """
    pass
