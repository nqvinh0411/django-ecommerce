"""
Ví dụ áp dụng tối ưu hóa database cho các ứng dụng e-commerce.

File này cung cấp các ví dụ thực tế về cách áp dụng các tiện ích tối ưu hóa
cho các view và viewset trong dự án e-commerce.
"""

# Catalog app examples
def catalog_optimization_examples():
    """
    Ví dụ về cách áp dụng tối ưu hóa cho app catalog.
    
    Catalog thường có nhiều quan hệ phức tạp, vì vậy sử dụng tối ưu hóa để
    giảm thiểu số lượng truy vấn là rất quan trọng.
    """
    # 1. Optimize CategoryViewSet
    from rest_framework import viewsets
    from core.optimization.mixins import QueryOptimizationMixin, DeferUnusedFieldsMixin
    from core.optimization.decorators import auto_optimize_queryset, log_slow_queries

    class OptimizedCategoryViewSet(QueryOptimizationMixin, viewsets.ModelViewSet):
        """
        ViewSet tối ưu hóa cho Category model.
        
        - Tự động select_related cho parent
        - Tự động prefetch_related cho children và brands
        """
        # Your existing code here...
        select_related_fields = ['parent']
        prefetch_related_fields = ['children', 'brands']
        
        @log_slow_queries(threshold_ms=300)
        def list(self, request, *args, **kwargs):
            """Log các truy vấn chậm khi liệt kê danh mục."""
            return super().list(request, *args, **kwargs)
    
    # 2. Optimize ProductListView
    from django.views.generic import ListView
    from core.optimization.mixins import QueryOptimizationMixin, SliceQuerySetMixin

    class OptimizedProductListView(QueryOptimizationMixin, SliceQuerySetMixin, ListView):
        """
        ListView tối ưu hóa cho Product model.
        
        - Tự động select_related cho category và brand
        - Tự động prefetch_related cho tags, attributes và reviews
        - Cắt queryset dựa trên phân trang để tránh tải quá nhiều dữ liệu
        """
        # Your existing code here...
        select_related_fields = ['category', 'brand']
        prefetch_related_fields = ['tags', 'attribute_values__attribute', 'reviews']
        
        def get_context_data(self, **kwargs):
            """Add custom context data."""
            context = super().get_context_data(**kwargs)
            # Your existing code here...
            return context


# Inventory app examples
def inventory_optimization_examples():
    """
    Ví dụ về cách áp dụng tối ưu hóa cho app inventory.
    
    Inventory thường liên quan đến nhiều app khác như catalog, orders, và
    có thể gây ra vấn đề N+1 nếu không được tối ưu hóa.
    """
    # 1. Optimize StockItemViewSet
    from rest_framework import viewsets
    from core.optimization.mixins import QueryOptimizationMixin
    from core.optimization.decorators import select_related_fields, defer_fields

    class OptimizedStockItemViewSet(QueryOptimizationMixin, viewsets.ModelViewSet):
        """
        ViewSet tối ưu hóa cho StockItem model.
        
        - Tự động select_related cho product và warehouse
        - Defer các trường mô tả lớn của sản phẩm để giảm kích thước truy vấn
        """
        # Your existing code here...
        select_related_fields = ['product', 'warehouse']
        
        def get_queryset(self):
            """Get optimized queryset."""
            queryset = super().get_queryset()
            
            # Defer large product fields
            return queryset.defer(
                'product__description', 
                'product__meta_description', 
                'product__technical_details'
            )
    
    # 2. Optimize StockMovementViewSet
    from rest_framework import viewsets
    from core.optimization.mixins import QueryOptimizationMixin
    from core.optimization.decorators import log_slow_queries

    class OptimizedStockMovementViewSet(QueryOptimizationMixin, viewsets.ModelViewSet):
        """
        ViewSet tối ưu hóa cho StockMovement model.
        
        - Tự động select_related cho stock_item, stock_item__product, stock_item__warehouse
        - Tự động prefetch_related cho audit_logs
        - Log các truy vấn chậm khi liệt kê để theo dõi hiệu suất
        """
        # Your existing code here...
        select_related_fields = ['stock_item', 'stock_item__product', 'stock_item__warehouse']
        prefetch_related_fields = ['audit_logs']
        
        @log_slow_queries(threshold_ms=500)
        def list(self, request, *args, **kwargs):
            """Log các truy vấn chậm khi liệt kê."""
            return super().list(request, *args, **kwargs)


# Orders app examples
def orders_optimization_examples():
    """
    Ví dụ về cách áp dụng tối ưu hóa cho app orders.
    
    Orders thường có nhiều quan hệ phức tạp với users, products, payments,
    và có thể gây ra vấn đề hiệu suất nếu không được tối ưu hóa.
    """
    # 1. Optimize OrderViewSet
    from rest_framework import viewsets
    from core.optimization.mixins import QueryOptimizationMixin, CountOptimizedPaginationMixin
    from core.optimization.decorators import auto_optimize_queryset

    class OptimizedOrderViewSet(QueryOptimizationMixin, CountOptimizedPaginationMixin, viewsets.ModelViewSet):
        """
        ViewSet tối ưu hóa cho Order model.
        
        - Tự động select_related cho user, shipping_address, billing_address
        - Tự động prefetch_related cho order_items, order_items__product
        - Tối ưu hóa count query trong phân trang để tăng hiệu suất
        """
        # Your existing code here...
        select_related_fields = ['user', 'shipping_address', 'billing_address']
        prefetch_related_fields = ['order_items', 'order_items__product', 'payments']
        
        def get_queryset(self):
            """Get optimized queryset with additional filtering."""
            queryset = super().get_queryset()
            
            # Apply additional filters
            if self.request.query_params.get('status'):
                queryset = queryset.filter(status=self.request.query_params.get('status'))
                
            return queryset
    
    # 2. Optimize OrderDetailView
    from django.views.generic import DetailView
    from core.optimization.mixins import QueryOptimizationMixin

    class OptimizedOrderDetailView(QueryOptimizationMixin, DetailView):
        """
        DetailView tối ưu hóa cho Order model.
        
        - Tối ưu hóa tất cả các quan hệ để tránh truy vấn N+1
        - Hữu ích cho dashboard hoặc chi tiết đơn hàng phức tạp
        """
        # Your existing code here...
        select_related_fields = ['user', 'shipping_address', 'billing_address']
        prefetch_related_fields = [
            'order_items', 
            'order_items__product', 
            'order_items__product__category',
            'payments'
        ]


# User profiles and custom models examples
def user_profile_optimization_examples():
    """
    Ví dụ về cách áp dụng tối ưu hóa cho user profiles.
    
    User profiles thường có nhiều thông tin liên quan và có thể
    được truy cập thường xuyên nên tối ưu hóa là rất quan trọng.
    """
    # 1. Optimize UserProfileViewSet
    from rest_framework import viewsets
    from core.optimization.mixins import QueryOptimizationMixin, DeferUnusedFieldsMixin
    from core.optimization.decorators import cached_property_with_ttl

    class OptimizedUserProfileViewSet(QueryOptimizationMixin, DeferUnusedFieldsMixin, viewsets.ModelViewSet):
        """
        ViewSet tối ưu hóa cho UserProfile model.
        
        - Tự động select_related cho user
        - Defer các trường lớn không thường xuyên sử dụng
        - Cached properties cho các tính toán phức tạp
        """
        # Your existing code here...
        select_related_fields = ['user']
        fields_to_defer = ['biography', 'preferences_json']
        
        # Có thể thêm các thuộc tính được cache vào model:
        """
        # Trong UserProfile model:
        @cached_property_with_ttl(ttl=3600)  # Cache trong 1 giờ
        def order_count(self):
            return self.user.orders.count()
            
        @cached_property_with_ttl(ttl=86400)  # Cache trong 1 ngày
        def total_spent(self):
            from django.db.models import Sum
            return self.user.orders.filter(status='completed').aggregate(
                Sum('total_amount')
            )['total_amount__sum'] or 0
        """


# Dashboard and analytics examples
def dashboard_optimization_examples():
    """
    Ví dụ về cách áp dụng tối ưu hóa cho các view dashboard và analytics.
    
    Dashboard thường yêu cầu nhiều truy vấn phức tạp và tổng hợp dữ liệu,
    vì vậy tối ưu hóa là cần thiết để tránh việc trang bị chậm.
    """
    # 1. Optimize SalesDashboardView
    from django.views.generic import TemplateView
    from core.optimization.utils import count_database_queries

    class OptimizedSalesDashboardView(TemplateView):
        """Dashboard view tối ưu hóa cho hiển thị dữ liệu bán hàng."""
        # Your existing code here...
        
        @count_database_queries
        def get_context_data(self, **kwargs):
            """
            Get context data with optimized queries.
            
            @count_database_queries sẽ ghi lại số lượng truy vấn được thực thi,
            giúp chúng ta theo dõi và tối ưu hóa khi cần thiết.
            """
            context = super().get_context_data(**kwargs)
            
            # Sử dụng tổng hợp DB để giảm thiểu truy vấn
            from django.db.models import Count, Sum, Avg
            from django.db.models.functions import TruncDay
            
            # Ví dụ: Tổng hợp doanh số bán hàng theo ngày
            from datetime import timedelta
            from django.utils import timezone
            
            end_date = timezone.now()
            start_date = end_date - timedelta(days=30)
            
            # Giả sử chúng ta có model Order
            """
            sales_data = Order.objects.filter(
                created_at__range=[start_date, end_date],
                status='completed'
            ).annotate(
                day=TruncDay('created_at')
            ).values('day').annotate(
                total_sales=Sum('total_amount'),
                order_count=Count('id'),
                avg_order_value=Avg('total_amount')
            ).order_by('day')
            
            context['sales_data'] = sales_data
            """
            
            return context


# Search and filter examples
def search_optimization_examples():
    """
    Ví dụ về cách áp dụng tối ưu hóa cho các view tìm kiếm và lọc.
    
    Tìm kiếm thường yêu cầu truy vấn phức tạp và có thể chậm nếu không được tối ưu hóa.
    """
    # 1. Optimize ProductSearchView
    from django.views.generic import ListView
    from core.optimization.mixins import QueryOptimizationMixin, SliceQuerySetMixin

    class OptimizedProductSearchView(QueryOptimizationMixin, SliceQuerySetMixin, ListView):
        """
        ListView tối ưu hóa cho tìm kiếm sản phẩm.
        
        - Tự động select_related và prefetch_related
        - Tối ưu hóa cho việc lọc và tìm kiếm với annotate
        """
        # Your existing code here...
        select_related_fields = ['category', 'brand']
        prefetch_related_fields = ['tags', 'reviews']
        
        def get_queryset(self):
            queryset = super().get_queryset()
            
            # Lấy tham số tìm kiếm
            search_query = self.request.GET.get('q', '')
            category = self.request.GET.get('category', '')
            price_min = self.request.GET.get('price_min', '')
            price_max = self.request.GET.get('price_max', '')
            
            # Áp dụng các bộ lọc
            if search_query:
                """
                from django.db.models import Q
                queryset = queryset.filter(
                    Q(name__icontains=search_query) |
                    Q(description__icontains=search_query) |
                    Q(category__name__icontains=search_query) |
                    Q(brand__name__icontains=search_query)
                )
                """
                
            # Áp dụng các bộ lọc bổ sung
            if category:
                queryset = queryset.filter(category__slug=category)
                
            if price_min:
                queryset = queryset.filter(price__gte=float(price_min))
                
            if price_max:
                queryset = queryset.filter(price__lte=float(price_max))
                
            # Sử dụng annotate để tính rating và số lượng đánh giá
            """
            from django.db.models import Avg, Count
            queryset = queryset.annotate(
                avg_rating=Avg('reviews__rating'),
                review_count=Count('reviews')
            )
            """
                
            return queryset


# Cache examples
def cache_optimization_examples():
    """
    Ví dụ về cách áp dụng cache cho tối ưu hóa.
    
    Kết hợp cache với tối ưu hóa truy vấn có thể cải thiện hiệu suất đáng kể.
    """
    # 1. Kết hợp cached_property_with_ttl với models
    from core.optimization.decorators import cached_property_with_ttl
    
    """
    class Product(models.Model):
        # Model fields here...
        
        @cached_property_with_ttl(ttl=3600)  # Cache for 1 hour
        def rating_summary(self):
            # Expensive calculation
            from django.db.models import Avg, Count, Sum
            result = self.reviews.aggregate(
                avg_rating=Avg('rating'),
                review_count=Count('id'),
                five_star=Sum(Case(When(rating=5, then=1), default=0, output_field=IntegerField())),
                four_star=Sum(Case(When(rating=4, then=1), default=0, output_field=IntegerField())),
                three_star=Sum(Case(When(rating=3, then=1), default=0, output_field=IntegerField())),
                two_star=Sum(Case(When(rating=2, then=1), default=0, output_field=IntegerField())),
                one_star=Sum(Case(When(rating=1, then=1), default=0, output_field=IntegerField()))
            )
            return result
    """
    
    # 2. View với Django's cache decorators
    """
    from django.views.decorators.cache import cache_page
    from django.utils.decorators import method_decorator
    
    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def top_products_view(request):
        # Truy vấn đắt đỏ để lấy sản phẩm hàng đầu
        products = Product.objects.annotate(
            sold_count=Count('order_items')
        ).order_by('-sold_count')[:10]
        
        return render(request, 'products/top_products.html', {'products': products})
    """


# Security related optimizations
def security_optimization_examples():
    """
    Ví dụ về các tối ưu hóa liên quan đến bảo mật.
    
    Các tối ưu hóa không chỉ cải thiện hiệu suất mà còn có thể giúp
    tăng cường bảo mật bằng cách giảm thiểu tiêu thụ tài nguyên.
    """
    # Rate limiting với tối ưu hóa truy vấn
    """
    from rest_framework.throttling import UserRateThrottle
    from core.optimization.mixins import QueryOptimizationMixin
    
    class CustomUserRateThrottle(UserRateThrottle):
        rate = '100/day'
        
    class SecureApiViewSet(QueryOptimizationMixin, viewsets.ModelViewSet):
        throttle_classes = [CustomUserRateThrottle]
        select_related_fields = ['user', 'category']
        prefetch_related_fields = ['permissions']
    """
    
    # Giới hạn độ sâu của prefetch_related để tránh tấn công DoS
    """
    class SafeQueryOptimizationMixin(QueryOptimizationMixin):
        # Giới hạn độ sâu của các quan hệ để tránh tấn công
        max_select_related_depth = 2
        
        # Nếu số lượng quan hệ vượt quá giới hạn, tắt tự động tối ưu hóa
        def get_queryset(self):
            queryset = super().get_queryset()
            model = queryset.model
            
            # Đếm tổng số quan hệ
            relation_count = 0
            for field in model._meta.get_fields():
                if field.is_relation:
                    relation_count += 1
                    
            # Nếu quá nhiều quan hệ, tắt tự động tối ưu hóa
            if relation_count > 20:
                self.disable_automatic_optimization = True
                
            return queryset
    """
