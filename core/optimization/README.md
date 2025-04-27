# Database Optimization Module

Các công cụ tối ưu hóa cơ sở dữ liệu cho dự án Django e-commerce.

## Tổng quan

Module này cung cấp nhiều tiện ích để tối ưu hóa truy vấn cơ sở dữ liệu, tập trung vào việc giảm bớt số lượng truy vấn qua các kỹ thuật như `select_related`, `prefetch_related`, `defer`, và `only`. Các công cụ này đặc biệt hữ ích cho các ứng dụng có thể mở rộng với nhiều quan hệ giữa các model.

## Thành phần

Module này bao gồm ba thành phần chính:

1. **Mixins** - Các mixin có thể áp dụng cho các view và viewset để tự động tối ưu hóa truy vấn.
2. **Decorators** - Các decorator có thể áp dụng cho các method cụ thể để tối ưu hóa truy vấn.
3. **Utility Functions** - Các hàm tiện ích cho việc phát hiện các trường quan hệ và tối ưu hóa truy vấn.

## Cách sử dụng

### Sử dụng Mixins

```python
from core.optimization.mixins import QueryOptimizationMixin, DeferUnusedFieldsMixin

class ProductListView(QueryOptimizationMixin, ListView):
    model = Product
    template_name = 'products/list.html'
    
    # Các trường được chỉ định rõ cho select_related
    select_related_fields = ['category', 'brand']
    
    # Các trường được chỉ định rõ cho prefetch_related
    prefetch_related_fields = ['tags', 'reviews']


class ProductDetailView(QueryOptimizationMixin, DeferUnusedFieldsMixin, DetailView):
    model = Product
    template_name = 'products/detail.html'
    
    # Chỉ tải những trường này, defer tất cả các trường khác
    fields_to_include = ['id', 'name', 'slug', 'price', 'description', 'category', 'brand']
```

### Sử dụng cho DRF ViewSets

```python
from rest_framework import viewsets
from core.optimization.mixins import QueryOptimizationMixin

class ProductViewSet(QueryOptimizationMixin, viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    # Tự động tối ưu hóa truy vấn dựa trên các mối quan hệ của model
    # Có thể điều chỉnh độ sâu của select_related
    max_select_related_depth = 2
    
    # Thêm các trường bổ sung nếu cần
    select_related_fields = ['created_by']
    prefetch_related_fields = ['variants']
```

### Sử dụng Decorators

```python
from core.optimization.decorators import (
    select_related_fields, prefetch_related_fields, 
    auto_optimize_queryset, log_slow_queries
)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    @select_related_fields('customer', 'shipping_address')
    @prefetch_related_fields('items', 'items__product')
    def get_queryset(self):
        return super().get_queryset()
    
    # Tự động phát hiện và tối ưu hóa các mối quan hệ
    @auto_optimize_queryset(max_select_depth=2)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    # Ghi lại các truy vấn chậm
    @log_slow_queries(threshold_ms=200)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
```

### Sử dụng Utility Functions

```python
from core.optimization.utils import optimize_queryset, count_database_queries

# Tối ưu hóa queryset với nhiều kỹ thuật khác nhau
queryset = optimize_queryset(
    Product.objects.all(),
    select_fields=['category', 'brand'],
    prefetch_fields=['tags', 'reviews'],
    defer_fields=['full_description', 'meta_data']
)

# Đếm số lượng truy vấn trong một hàm
@count_database_queries
def get_dashboard_data(request):
    # Code xử lý nhiều truy vấn
    return response
```

### Sử dụng Cached Property với TTL

```python
from core.optimization.decorators import cached_property_with_ttl

class Product(models.Model):
    name = models.CharField(max_length=100)
    # Các trường khác...
    
    @cached_property_with_ttl(ttl=3600)  # Cache trong 1 giờ
    def average_rating(self):
        # Tính toán phức tạp / tốn nhiều tài nguyên
        return self.reviews.aggregate(Avg('rating'))['rating__avg']
```

## Tính năng chính

1. **Tự động tối ưu hóa quan hệ**
   - Tự động phát hiện và áp dụng `select_related` và `prefetch_related` dựa trên cấu trúc model

2. **Tối ưu hóa tải trường**
   - Sử dụng `defer` để trì hoãn việc tải các trường lớn
   - Sử dụng `only` để chỉ tải các trường cần thiết

3. **Tối ưu hóa phân trang**
   - Cắt queryset dựa trên cài đặt phân trang để tránh tải dữ liệu không cần thiết
   - Tối ưu hóa truy vấn count cho phân trang

4. **Ghi lại và phân tích**
   - Ghi lại các truy vấn chậm để phát hiện vấn đề hiệu suất
   - Đếm số lượng truy vấn để phát hiện vấn đề N+1

## Thực tiễn tốt nhất

1. **Sử dụng mixins cho các view phổ biến**
   - Áp dụng `QueryOptimizationMixin` cho các view liệt kê
   - Áp dụng `DeferUnusedFieldsMixin` cho các view có nhiều trường lớn

2. **Sử dụng decorators cho các method cụ thể**
   - Sử dụng `select_related_fields` và `prefetch_related_fields` cho các method cụ thể
   - Sử dụng `log_slow_queries` cho các endpoint có khả năng có vấn đề hiệu suất

3. **Sử dụng cached_property_with_ttl cho các tính toán phức tạp**
   - Áp dụng cho các method tính toán phức tạp trên model
   - Thiết lập TTL phù hợp dựa trên tần suất thay đổi dữ liệu

4. **Theo dõi và đo lường hiệu suất**
   - Sử dụng `count_database_queries` để phát hiện số lượng truy vấn tăng đột biến
   - Xem log để phát hiện các truy vấn chậm và tối ưu hóa chúng

## Hướng dẫn chi tiết theo tình huống

### 1. Giải quyết vấn đề N+1 query

Vấn đề N+1 xảy ra khi bạn truy cập một danh sách các object, sau đó truy cập các quan hệ của từng object trong vòng lặp, gây ra nhiều truy vấn không cần thiết.

#### Phát hiện vấn đề N+1:

```python
# Đặt decorator này ở view hoặc method để phát hiện N+1 query
from core.optimization.utils import count_database_queries

@count_database_queries
def product_list_view(request):
    products = Product.objects.all()[:10]
    
    # N+1 query problem:
    for product in products:
        print(f"Product {product.name} has category: {product.category.name}")
        print(f"Product has {product.reviews.count()} reviews")
    
    return render(request, 'products/list.html', {'products': products})
```

#### Giải pháp:

```python
from core.optimization.mixins import QueryOptimizationMixin

class ProductListView(QueryOptimizationMixin, ListView):
    model = Product
    template_name = 'products/list.html'
    
    select_related_fields = ['category', 'brand']
    prefetch_related_fields = ['reviews', 'tags']
```

### 2. Tối ưu hóa cho API endpoint có nhiều lọc và sắp xếp

```python
from core.optimization.mixins import QueryOptimizationMixin
from core.optimization.decorators import log_slow_queries

class ProductViewSet(QueryOptimizationMixin, viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    select_related_fields = ['category', 'brand']
    prefetch_related_fields = ['tags']
    
    @log_slow_queries(threshold_ms=300)
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Lọc theo các tham số từ request
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
            
        price_min = self.request.query_params.get('price_min')
        if price_min:
            queryset = queryset.filter(price__gte=float(price_min))
            
        # Sắp xếp
        ordering = self.request.query_params.get('ordering', '-created_at')
        queryset = queryset.order_by(ordering)
        
        return queryset
```

### 3. Tối ưu hóa truy vấn thống kê và báo cáo

```python
from core.optimization.decorators import cached_property_with_ttl
from django.db.models import Sum, Avg, Count
from django.db.models.functions import TruncDate

class DashboardView(TemplateView):
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Sử dụng annotate để tính toán thống kê trong một truy vấn duy nhất
        order_stats = Order.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            total_sales=Sum('total_amount'),
            order_count=Count('id'),
            average_order=Avg('total_amount')
        ).order_by('date')
        
        context['order_stats'] = order_stats
        return context

# Trong model, sử dụng cached_property_with_ttl cho các tính toán phức tạp
class Product(models.Model):
    # fields...
    
    @cached_property_with_ttl(ttl=3600)  # Cache trong 1 giờ
    def sales_stats(self):
        return OrderItem.objects.filter(
            product=self,
            order__status='completed'
        ).aggregate(
            total_sold=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('price')),
            order_count=Count('order', distinct=True)
        )
```

### 4. Tối ưu hóa cho trang chi tiết nhiều dữ liệu

```python
from core.optimization.mixins import QueryOptimizationMixin, DeferUnusedFieldsMixin

class ProductDetailView(QueryOptimizationMixin, DeferUnusedFieldsMixin, DetailView):
    model = Product
    template_name = 'products/detail.html'
    
    # Tối ưu select_related rất hiệu quả cho trang chi tiết
    select_related_fields = [
        'category', 'brand', 'primary_image', 'created_by'
    ]
    
    # Prefetch_related cho các quan hệ M2M và reverse
    prefetch_related_fields = [
        'images', 'tags', 'attribute_values__attribute',
        'reviews__user', 'related_products'
    ]
    
    # Chỉ tải các trường cần thiết, trì hoãn các trường lớn
    fields_to_defer = [
        'technical_specifications', 'seo_description', 
        'long_html_description'
    ]
```

### 5. Tối ưu hóa cho Inventory Management

```python
from core.optimization.mixins import QueryOptimizationMixin
from core.optimization.decorators import select_related_fields, prefetch_related_fields

class StockItemListView(QueryOptimizationMixin, ListView):
    model = StockItem
    template_name = 'inventory/stock_items.html'
    paginate_by = 50
    
    select_related_fields = ['product', 'warehouse']
    prefetch_related_fields = ['movements']
    
    # Với queryset phức tạp, bạn có thể ghi đè get_queryset
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Thêm annotate để tính số lượng tồn kho hiện tại
        queryset = queryset.annotate(
            current_stock=F('initial_quantity') + Coalesce(
                Sum(
                    Case(
                        When(movements__movement_type='IN', then=F('movements__quantity')),
                        When(movements__movement_type='OUT', then=-F('movements__quantity')),
                        default=0,
                        output_field=IntegerField()
                    )
                ),
                0
            )
        )
        
        # Filtrering
        status = self.request.GET.get('status')
        if status == 'low_stock':
            queryset = queryset.filter(current_stock__lte=F('minimum_stock'))
        elif status == 'out_of_stock':
            queryset = queryset.filter(current_stock=0)
            
        return queryset
```

## Các kỹ thuật kết hợp

### 1. Kết hợp nhiều mixins

```python
from core.optimization.mixins import (
    QueryOptimizationMixin, DeferUnusedFieldsMixin,
    SliceQuerySetMixin, CountOptimizedPaginationMixin
)

class OrderListView(
    QueryOptimizationMixin,
    DeferUnusedFieldsMixin,
    SliceQuerySetMixin,
    CountOptimizedPaginationMixin,
    ListView
):
    model = Order
    template_name = 'orders/list.html'
    paginate_by = 25
    
    select_related_fields = ['user', 'shipping_address', 'billing_address']
    prefetch_related_fields = ['items', 'payments']
    fields_to_defer = ['notes', 'admin_notes', 'full_payment_details']
```

### 2. Kết hợp Django Debug Toolbar

Django Debug Toolbar là công cụ rất hữ ích để phát hiện vấn đề hiệu suất cơ sở dữ liệu. Kết hợp với module tối ưu hóa:

```python
# settings.py (development)
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

# Kết hợp với log_slow_queries
from core.optimization.decorators import log_slow_queries

@log_slow_queries(threshold_ms=500)
def problematic_view(request):
    # Logic View - Debug Toolbar sẽ hiển thị các truy vấn
    # và log_slow_queries sẽ ghi lại các truy vấn chậm
    return response
```

### 3. Đo lường hiệu suất trước và sau khi tối ưu hóa

```python
from core.optimization.utils import count_database_queries
from django.utils import timezone
import time

def benchmark_view():
    # Trước khi tối ưu hóa
    start_time = time.time()
    with count_database_queries() as query_count:
        list_before = list(Product.objects.all()[:100])
        for product in list_before:
            # Gây ra vấn đề N+1
            category_name = product.category.name
    time_before = time.time() - start_time
    
    # Sau khi tối ưu hóa
    start_time = time.time()
    with count_database_queries() as query_count:
        list_after = list(
            Product.objects.select_related('category').all()[:100]
        )
        for product in list_after:
            # Không còn vấn đề N+1
            category_name = product.category.name
    time_after = time.time() - start_time
    
    print(f"Trước: {len(query_count)} truy vấn, {time_before:.2f}s")
    print(f"Sau: {len(query_count)} truy vấn, {time_after:.2f}s")
    print(f"Cải thiện: {time_before/time_after:.2f}x nhanh hơn")
```

## Tối ưu hóa cho ứng dụng cụ thể

### Tối ưu hóa cho Catalog

```python
from core.optimization.mixins import QueryOptimizationMixin
from core.optimization.decorators import auto_optimize_queryset

class CategoryViewSet(QueryOptimizationMixin, viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    select_related_fields = ['parent']
    prefetch_related_fields = ['children', 'products']
    
    # Tài nguyên cho trang danh mục - tránh các truy vấn không cần thiết
    @auto_optimize_queryset(max_select_depth=2)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
        
class ProductFilterView(QueryOptimizationMixin, ListView):
    model = Product
    template_name = 'products/filter.html'
    
    # Tối ưu hóa cho bộ lọc phức tạp
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Sử dụng các truy vấn tổng hợp để giảm thiểu số lượng truy vấn
        queryset = queryset.annotate(
            review_count=Count('reviews'),
            average_rating=Avg('reviews__rating')
        )
        
        # Áp dụng bộ lọc phức tạp
        # ...
        
        return queryset
```

### Tối ưu hóa cho Orders

```python
from core.optimization.mixins import QueryOptimizationMixin
from core.optimization.decorators import log_slow_queries

class OrderViewSet(QueryOptimizationMixin, viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    select_related_fields = ['user', 'shipping_address', 'billing_address'] 
    prefetch_related_fields = [
        'items', 'items__product', 'payments', 'status_history'
    ]
    
    # Theo dõi hiệu suất truy vấn cụ thể
    @log_slow_queries(threshold_ms=500)
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Lọc theo trạng thái, ngày đặt hàng, khách hàng, v.v.
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # Tìm kiếm
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(id__icontains=search) |
                Q(user__email__icontains=search) |
                Q(user__phone_number__icontains=search)
            )
            
        return queryset
```

## Kịch bản nâng cao

### 1. Tối ưu hóa khối lượng công việc nhiều ngôn ngữ (i18n)

```python
from core.optimization.mixins import QueryOptimizationMixin, DeferUnusedFieldsMixin
from core.optimization.decorators import cached_property_with_ttl

class MultilangProductView(QueryOptimizationMixin, DeferUnusedFieldsMixin):
    select_related_fields = ['category', 'brand']
    prefetch_related_fields = ['translations']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Tối ưu hóa cho tải các bản dịch
        current_language = translation.get_language()
        
        # Sử dụng Prefetch để chỉ tải các bản dịch cho ngôn ngữ hiện tại
        from django.db.models import Prefetch
        queryset = queryset.prefetch_related(
            Prefetch(
                'translations',
                queryset=ProductTranslation.objects.filter(language_code=current_language),
                to_attr='current_translations'
            )
        )
        
        return queryset
```

### 2. Tối ưu hóa cho các ứng dụng có sử dụng permissions phức tạp

```python
from core.optimization.mixins import QueryOptimizationMixin 
from core.optimization.decorators import cached_property_with_ttl

class UserPermissionOptimizedView(QueryOptimizationMixin, APIView):
    permission_classes = [IsAuthenticated]
    
    select_related_fields = ['profile']
    prefetch_related_fields = ['groups', 'user_permissions']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Sử dụng Prefetch để tải trước tất cả permissions liên quan
        from django.db.models import Prefetch
        queryset = queryset.prefetch_related(
            Prefetch(
                'groups__permissions',
                queryset=Permission.objects.select_related('content_type'),
                to_attr='all_group_permissions'
            )
        )
        
        return queryset

# Trong model User
class User(AbstractUser):
    # ...
    
    @cached_property_with_ttl(ttl=3600)  # Cache trong 1 giờ
    def all_permissions(self):
        """Trả về tất cả permissions, tối ưu hóa cho kiểm tra quyền thường xuyên"""
        if not hasattr(self, '_permissions_cache'):
            perms = set()
            
            # Permissions trực tiếp
            for perm in self.user_permissions.all():
                perms.add(f"{perm.content_type.app_label}.{perm.codename}")
                
            # Permissions từ group
            for group in self.groups.all():
                for perm in group.permissions.all():
                    perms.add(f"{perm.content_type.app_label}.{perm.codename}")
                    
            self._permissions_cache = perms
            
        return self._permissions_cache
```

## Hướng dẫn debug hiệu suất

### 1. Sử dụng Context Manager để đo lường hiệu suất

```python
from core.optimization.utils import count_database_queries
from django.utils import timezone
import time

def complex_view(request):
    # Sử dụng context manager để đo lường
    with count_database_queries() as query_count:
        # Phần 1: Tải sản phẩm
        start_time = time.time()
        products = Product.objects.filter(
            # conditions
        ).select_related('category', 'brand')
        products_time = time.time() - start_time
        
        # Phần 2: Tải đơn hàng
        start_time = time.time()
        orders = Order.objects.filter(
            # conditions
        ).select_related('user')
        orders_time = time.time() - start_time
        
    # Log kết quả đo lường
    print(f"Tổng số truy vấn: {query_count}")
    print(f"Thời gian tải sản phẩm: {products_time:.2f}s")
    print(f"Thời gian tải đơn hàng: {orders_time:.2f}s")
    
    # Tiếp tục xử lý...
```

### 2. Tạo decorator tùy chỉnh để phân tích hiệu suất

```python
def analyze_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Đo lường trước khi tối ưu hóa
        start_time = time.time()
        with connection.execute_wrapper(QueryCounter()) as counter:
            result = func(*args, **kwargs)
        
        # Log kết quả
        execution_time = time.time() - start_time
        query_count = counter.queries
        
        # Log to file or monitoring system
        if query_count > 10 or execution_time > 1.0:
            logger.warning(
                f"Hiệu suất thấp trong {func.__name__}: "
                f"{query_count} truy vấn, {execution_time:.2f}s"
            )
            
        return result
    return wrapper

# Sử dụng
@analyze_performance
def expensive_view(request):
    # Logic view
    pass
