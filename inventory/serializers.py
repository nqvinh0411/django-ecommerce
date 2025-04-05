from rest_framework import serializers
from products.models import Product
from .models import Warehouse, StockItem, StockMovement, InventoryAuditLog


class WarehouseSerializer(serializers.ModelSerializer):
    """
    Serializer cho model Warehouse, xử lý thông tin kho hàng.
    
    Attributes:
        name (str): Tên kho hàng
        location (str): Vị trí kho hàng
        description (str): Mô tả chi tiết về kho hàng
        is_default (bool): Xác định có phải kho mặc định hay không
        is_active (bool): Xác định kho còn hoạt động hay không
    """
    stock_items_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Warehouse
        fields = [
            'id', 'name', 'location', 'description', 'is_default', 'is_active', 
            'stock_items_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_stock_items_count(self, obj):
        """Đếm số lượng items trong kho"""
        return obj.stock_items.count()
    
    def validate_name(self, value):
        """Validate tên kho hàng không được trùng"""
        instance = getattr(self, 'instance', None)
        if instance and instance.name == value:
            return value
            
        if Warehouse.objects.filter(name=value).exists():
            raise serializers.ValidationError("Tên kho hàng đã tồn tại")
        return value
    
    def validate(self, data):
        """Validate toàn bộ data"""
        # Nếu đánh dấu là kho mặc định, các kho khác phải được cập nhật
        if data.get('is_default', False):
            instance = getattr(self, 'instance', None)
            if not instance or not instance.is_default:
                # Sẽ được xử lý bởi view
                pass
        return data


class ProductNestedSerializer(serializers.Serializer):
    """
    Serializer lồng đơn giản cho model Product để hiển thị trong StockItem
    """
    id = serializers.IntegerField()
    name = serializers.CharField()
    sku = serializers.CharField(required=False)
    
    class Meta:
        fields = ['id', 'name', 'sku']


class WarehouseNestedSerializer(serializers.ModelSerializer):
    """
    Serializer lồng đơn giản cho model Warehouse để hiển thị trong StockItem
    """
    class Meta:
        model = Warehouse
        fields = ['id', 'name', 'location', 'is_active']


class StockItemSerializer(serializers.ModelSerializer):
    """
    Serializer cho model StockItem, xử lý thông tin sản phẩm trong kho.
    
    Attributes:
        product (ProductNestedSerializer): Thông tin sản phẩm
        warehouse (WarehouseNestedSerializer): Thông tin kho hàng
        quantity (int): Số lượng sản phẩm trong kho
        low_stock_threshold (int): Ngưỡng cảnh báo hết hàng
        is_tracked (bool): Xác định sản phẩm có được theo dõi số lượng hay không
    """
    product = ProductNestedSerializer(read_only=True)
    warehouse = WarehouseNestedSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    warehouse_id = serializers.IntegerField(write_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    stock_status = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = StockItem
        fields = [
            'id', 'product', 'product_id', 'warehouse', 'warehouse_id', 
            'quantity', 'low_stock_threshold', 'is_tracked', 'is_low_stock',
            'stock_status', 'last_updated', 'created_at'
        ]
        read_only_fields = ['id', 'last_updated', 'created_at', 'is_low_stock', 'stock_status']
    
    def get_stock_status(self, obj):
        """Lấy trạng thái tồn kho của sản phẩm"""
        if not obj.is_tracked:
            return "untracked"
        if obj.quantity <= 0:
            return "out_of_stock"
        if obj.quantity <= obj.low_stock_threshold:
            return "low_stock"
        return "in_stock"
    
    def validate_product_id(self, value):
        """Validate sản phẩm tồn tại"""
        try:
            Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Sản phẩm không tồn tại")
        return value
    
    def validate_warehouse_id(self, value):
        """Validate kho hàng tồn tại và đang hoạt động"""
        try:
            warehouse = Warehouse.objects.get(id=value)
            if not warehouse.is_active:
                raise serializers.ValidationError("Kho hàng không hoạt động")
        except Warehouse.DoesNotExist:
            raise serializers.ValidationError("Kho hàng không tồn tại")
        return value
    
    def validate_quantity(self, value):
        """Validate số lượng không âm"""
        if value < 0:
            raise serializers.ValidationError("Số lượng không thể là số âm")
        return value
    
    def validate_low_stock_threshold(self, value):
        """Validate ngưỡng hết hàng không âm"""
        if value < 0:
            raise serializers.ValidationError("Ngưỡng hết hàng không thể là số âm")
        return value
    
    def validate(self, data):
        """Validate sản phẩm không trùng lặp trong cùng một kho"""
        instance = getattr(self, 'instance', None)
        product_id = data.get('product_id')
        warehouse_id = data.get('warehouse_id')
        
        if product_id and warehouse_id:
            # Kiểm tra khi tạo mới
            if not instance and StockItem.objects.filter(product_id=product_id, warehouse_id=warehouse_id).exists():
                raise serializers.ValidationError({"non_field_errors": ["Sản phẩm này đã tồn tại trong kho hàng đã chọn"]})
            # Kiểm tra khi cập nhật
            elif instance and instance.product_id != product_id and instance.warehouse_id != warehouse_id:
                if StockItem.objects.filter(product_id=product_id, warehouse_id=warehouse_id).exists():
                    raise serializers.ValidationError({"non_field_errors": ["Sản phẩm này đã tồn tại trong kho hàng đã chọn"]})
        
        return data


class StockMovementSerializer(serializers.ModelSerializer):
    """
    Serializer cho model StockMovement, xử lý thông tin di chuyển hàng trong kho.
    
    Attributes:
        stock_item (StockItemSerializer): Thông tin sản phẩm trong kho
        movement_type (str): Loại di chuyển (nhập hàng, xuất hàng, điều chỉnh, v.v)
        quantity (int): Số lượng sản phẩm di chuyển
        reason (str): Lý do di chuyển
        related_order (Order): Đơn hàng liên quan (nếu có)
    """
    stock_item_id = serializers.IntegerField(write_only=True)
    stock_item = StockItemSerializer(read_only=True)
    movement_type_display = serializers.CharField(source='get_movement_type_display', read_only=True)
    related_order_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    product_name = serializers.SerializerMethodField(read_only=True)
    warehouse_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = StockMovement
        fields = [
            'id', 'stock_item', 'stock_item_id', 'movement_type', 'movement_type_display',
            'quantity', 'reason', 'related_order', 'related_order_id', 
            'created_by', 'created_by_username', 'product_name', 'warehouse_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'created_by', 'product_name', 'warehouse_name']
    
    def get_product_name(self, obj):
        """Lấy tên sản phẩm từ stock item"""
        if hasattr(obj.stock_item, 'product') and hasattr(obj.stock_item.product, 'name'):
            return obj.stock_item.product.name
        return str(obj.stock_item.product)
    
    def get_warehouse_name(self, obj):
        """Lấy tên kho hàng từ stock item"""
        if hasattr(obj.stock_item, 'warehouse') and hasattr(obj.stock_item.warehouse, 'name'):
            return obj.stock_item.warehouse.name
        return str(obj.stock_item.warehouse)
    
    def validate_stock_item_id(self, value):
        """Validate stock item tồn tại"""
        try:
            StockItem.objects.get(id=value)
        except StockItem.DoesNotExist:
            raise serializers.ValidationError("Sản phẩm trong kho không tồn tại")
        return value
    
    def validate_quantity(self, value):
        """Validate số lượng không bằng 0"""
        if value == 0:
            raise serializers.ValidationError("Số lượng phải khác 0")
        return value
    
    def validate(self, data):
        """Validate dữ liệu toàn bộ"""
        movement_type = data.get('movement_type')
        quantity = data.get('quantity', 0)
        
        # Kiểm tra số lượng dựa trên loại di chuyển
        if movement_type in ['receive', 'adjustment_add', 'return', 'transfer_in'] and quantity < 0:
            raise serializers.ValidationError({"quantity": ["Số lượng phải là số dương cho loại di chuyển này"]})
        
        if movement_type in ['ship', 'adjustment_subtract', 'waste', 'transfer_out'] and quantity > 0:
            # Chuyển số lượng thành số âm
            data['quantity'] = -abs(quantity)
        
        return data
    
    def create(self, validated_data):
        # Lấy người dùng hiện tại từ context
        user = self.context['request'].user if 'request' in self.context else None
        
        # Thêm người dùng vào trường created_by
        if user and not user.is_anonymous:
            validated_data['created_by'] = user
            
        return super().create(validated_data)


class InventoryAuditLogSerializer(serializers.ModelSerializer):
    """
    Serializer cho model InventoryAuditLog, ghi lại các thay đổi trong kho.
    
    Attributes:
        stock_item (StockItemSerializer): Thông tin sản phẩm trong kho
        change_type (str): Loại thay đổi
        changed_by (User): Người thực hiện thay đổi
        old_quantity (int): Số lượng trước khi thay đổi
        new_quantity (int): Số lượng sau khi thay đổi
        note (str): Ghi chú về thay đổi
    """
    stock_item = StockItemSerializer(read_only=True)
    change_type_display = serializers.CharField(source='get_change_type_display', read_only=True)
    changed_by_username = serializers.CharField(source='changed_by.username', read_only=True, allow_null=True)
    product_name = serializers.SerializerMethodField(read_only=True)
    warehouse_name = serializers.SerializerMethodField(read_only=True)
    quantity_change = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = InventoryAuditLog
        fields = [
            'id', 'stock_item', 'change_type', 'change_type_display', 
            'changed_by', 'changed_by_username', 'old_quantity', 'new_quantity', 
            'quantity_change', 'product_name', 'warehouse_name', 'note', 'created_at'
        ]
        read_only_fields = [
            'id', 'stock_item', 'change_type', 'changed_by', 'old_quantity', 
            'new_quantity', 'quantity_change', 'product_name', 'warehouse_name', 'created_at'
        ]
    
    def get_product_name(self, obj):
        """Lấy tên sản phẩm từ stock item"""
        if hasattr(obj.stock_item, 'product') and hasattr(obj.stock_item.product, 'name'):
            return obj.stock_item.product.name
        return None
    
    def get_warehouse_name(self, obj):
        """Lấy tên kho hàng từ stock item"""
        if hasattr(obj.stock_item, 'warehouse') and hasattr(obj.stock_item.warehouse, 'name'):
            return obj.stock_item.warehouse.name
        return None
    
    def get_quantity_change(self, obj):
        """Tính toán sự thay đổi số lượng"""
        return obj.new_quantity - obj.old_quantity