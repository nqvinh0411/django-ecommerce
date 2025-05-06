# Inventory App

## Mô tả
App `inventory` quản lý kho hàng, theo dõi tồn kho sản phẩm, di chuyển hàng hoá và kiểm toán hàng tồn kho trong hệ thống e-commerce. App này giúp doanh nghiệp quản lý chính xác lượng hàng tồn kho trên nhiều kho hàng khác nhau.

## Mô hình dữ liệu

### Warehouse
Quản lý thông tin kho hàng:
- `name`: Tên kho hàng
- `location`: Vị trí kho
- `description`: Mô tả chi tiết
- `is_default`: Đánh dấu là kho mặc định
- `is_active`: Trạng thái hoạt động
- `created_at`: Thời điểm tạo
- `updated_at`: Thời điểm cập nhật

### StockItem
Quản lý tồn kho sản phẩm trong các kho:
- `product`: Liên kết đến Product
- `warehouse`: Liên kết đến Warehouse
- `quantity`: Số lượng tồn kho
- `low_stock_threshold`: Ngưỡng cảnh báo tồn kho thấp
- `is_tracked`: Đánh dấu có theo dõi tồn kho
- `last_updated`: Thời điểm cập nhật cuối
- `created_at`: Thời điểm tạo
- `is_low_stock`: Thuộc tính tính toán kiểm tra tồn kho thấp

### StockMovement
Theo dõi di chuyển hàng tồn kho:
- `stock_item`: Liên kết đến StockItem
- `movement_type`: Loại di chuyển (IN, OUT, ADJUSTMENT)
- `quantity`: Số lượng di chuyển
- `reason`: Lý do di chuyển
- `related_order`: Liên kết đến Order (nếu có)
- `created_at`: Thời điểm di chuyển
- `created_by`: Người thực hiện di chuyển

### InventoryAuditLog
Ghi lại lịch sử thay đổi tồn kho:
- `stock_item`: Liên kết đến StockItem
- `change_type`: Loại thay đổi
- `old_quantity`: Số lượng trước khi thay đổi
- `new_quantity`: Số lượng sau khi thay đổi
- `changed_by`: Người thực hiện thay đổi
- `note`: Ghi chú thay đổi
- `created_at`: Thời điểm thay đổi

## API Endpoints & URLs

### Warehouse Endpoints

| URL | View | Method | Chức năng |
|-----|------|--------|-----------|
| `/api/inventory/warehouses/list` | WarehouseListView | GET | Liệt kê tất cả kho hàng |
| `/api/inventory/warehouses/create` | WarehouseCreateView | POST | Tạo một kho hàng mới |
| `/api/inventory/warehouses/{id}/detail` | WarehouseRetrieveView | GET | Xem chi tiết một kho hàng |
| `/api/inventory/warehouses/{id}/update` | WarehouseUpdateView | PUT/PATCH | Cập nhật một kho hàng |
| `/api/inventory/warehouses/{id}/delete` | WarehouseDestroyView | DELETE | Xóa một kho hàng |

### StockItem Endpoints

| URL | View | Method | Chức năng |
|-----|------|--------|-----------|
| `/api/inventory/stock-items/list` | StockItemListView | GET | Liệt kê tất cả sản phẩm trong kho |
| `/api/inventory/stock-items/create` | StockItemCreateView | POST | Tạo một sản phẩm mới trong kho |
| `/api/inventory/stock-items/{id}/detail` | StockItemRetrieveView | GET | Xem chi tiết một sản phẩm trong kho |
| `/api/inventory/stock-items/{id}/update` | StockItemUpdateView | PUT/PATCH | Cập nhật một sản phẩm trong kho |
| `/api/inventory/stock-items/{id}/delete` | StockItemDestroyView | DELETE | Xóa một sản phẩm trong kho |

### StockMovement Endpoints

| URL | View | Method | Chức năng |
|-----|------|--------|-----------|
| `/api/inventory/stock-movements/list` | StockMovementListView | GET | Liệt kê tất cả di chuyển kho |
| `/api/inventory/stock-movements/create` | StockMovementCreateView | POST | Tạo một di chuyển kho mới |
| `/api/inventory/stock-movements/{id}/detail` | StockMovementRetrieveView | GET | Xem chi tiết một di chuyển kho |

### Inventory Audit Log Endpoints

| URL | View | Method | Chức năng |
|-----|------|--------|-----------|
| `/api/inventory/audit-logs/list` | InventoryAuditLogListView | GET | Liệt kê tất cả log kiểm kê |
| `/api/inventory/audit-logs/{id}/detail` | InventoryAuditLogRetrieveView | GET | Xem chi tiết một log kiểm kê |

## Chi tiết về Views

### Warehouse Views

#### WarehouseListView
- **Kế thừa từ**: BaseListView
- **Chức năng**: Liệt kê tất cả kho hàng
- **Serializer**: WarehouseSerializer 
- **Quyền truy cập**: IsAdminUser (chỉ admin mới có thể truy cập)
- **Bộ lọc và sắp xếp**:
  - `filterset_fields`: ['is_default', 'is_active'] - Lọc theo kho mặc định và trạng thái hoạt động
  - `search_fields`: ['name', 'location', 'description'] - Tìm kiếm theo tên, địa điểm, và mô tả
  - `ordering_fields`: ['name', 'location', 'created_at'] - Sắp xếp theo tên, địa điểm, và thời gian tạo
  - `ordering`: ['name'] - Mặc định sắp xếp theo tên

#### WarehouseCreateView
- **Kế thừa từ**: BaseCreateView
- **Chức năng**: Tạo mới một kho hàng
- **Serializer**: WarehouseSerializer
- **Quyền truy cập**: IsAdminUser (chỉ admin mới có thể truy cập)
- **Logic xử lý**:
  - Nếu kho hàng mới được đánh dấu là kho mặc định, cập nhật các kho hàng khác để đảm bảo chỉ có một kho mặc định
  - Tạo kho hàng mới với các thông tin đã xác thực

#### WarehouseRetrieveView
- **Kế thừa từ**: BaseRetrieveView
- **Chức năng**: Xem chi tiết một kho hàng
- **Serializer**: WarehouseSerializer
- **Quyền truy cập**: IsAdminUser (chỉ admin mới có thể truy cập)

#### WarehouseUpdateView
- **Kế thừa từ**: BaseUpdateView
- **Chức năng**: Cập nhật một kho hàng
- **Serializer**: WarehouseSerializer
- **Quyền truy cập**: IsAdminUser (chỉ admin mới có thể truy cập)
- **Logic xử lý**:
  - Nếu kho hàng được đánh dấu là kho mặc định và trước đó không phải là mặc định, cập nhật các kho hàng khác để đảm bảo chỉ có một kho mặc định
  - Lưu các thay đổi vào kho hàng

#### WarehouseDestroyView
- **Kế thừa từ**: BaseDestroyView
- **Chức năng**: Xóa một kho hàng
- **Serializer**: WarehouseSerializer
- **Quyền truy cập**: IsAdminUser (chỉ admin mới có thể truy cập)

### StockItem Views

#### StockItemListView
- **Kế thừa từ**: BaseListView
- **Chức năng**: Liệt kê tất cả sản phẩm trong kho
- **Serializer**: StockItemSerializer
- **Quyền truy cập**: IsAdminUser (chỉ admin mới có thể truy cập)
- **Bộ lọc và sắp xếp**:
  - Lọc theo product, warehouse, is_active, low_stock
  - Tìm kiếm theo các trường quan trọng
  - Sắp xếp theo nhiều tiêu chí khác nhau

#### StockItemCreateView, StockItemRetrieveView, StockItemUpdateView, StockItemDestroyView
- **Quyền truy cập**: IsAdminUser (chỉ admin mới có thể truy cập)
- **Serializer**: StockItemSerializer
- **Chức năng**: Quản lý vòng đời của các sản phẩm trong kho

### StockMovement Views

#### StockMovementListView
- **Kế thừa từ**: BaseListView
- **Chức năng**: Liệt kê tất cả di chuyển kho
- **Serializer**: StockMovementSerializer
- **Quyền truy cập**: IsAdminUser (chỉ admin mới có thể truy cập)
- **Bộ lọc và sắp xếp**:
  - Lọc theo stock_item, movement_type, related_order
  - Tìm kiếm theo các trường quan trọng
  - Sắp xếp theo ngày tạo, mặc định là mới nhất trước

#### StockMovementCreateView
- **Kế thừa từ**: BaseCreateView
- **Chức năng**: Tạo mới một di chuyển kho
- **Serializer**: StockMovementSerializer
- **Quyền truy cập**: IsAdminUser (chỉ admin mới có thể truy cập)
- **Logic xử lý**:
  - Tự động cập nhật số lượng trong StockItem dựa trên loại di chuyển (nhập, xuất, điều chỉnh)
  - Tạo InventoryAuditLog để ghi lại thay đổi
  - Xác thực logic nghiệp vụ (ví dụ: đảm bảo không xuất quá số lượng tồn kho)

#### StockMovementRetrieveView
- **Kế thừa từ**: BaseRetrieveView
- **Chức năng**: Xem chi tiết một di chuyển kho
- **Serializer**: StockMovementSerializer
- **Quyền truy cập**: IsAdminUser (chỉ admin mới có thể truy cập)

### Inventory Audit Log Views

#### InventoryAuditLogListView
- **Kế thừa từ**: BaseListView
- **Chức năng**: Liệt kê tất cả log kiểm kê
- **Serializer**: InventoryAuditLogSerializer
- **Quyền truy cập**: IsAdminUser (chỉ admin mới có thể truy cập)
- **Bộ lọc và sắp xếp**:
  - Lọc theo stock_item, user, action_type
  - Tìm kiếm theo các trường quan trọng
  - Sắp xếp theo ngày tạo, mặc định là mới nhất trước

#### InventoryAuditLogRetrieveView
- **Kế thừa từ**: BaseRetrieveView
- **Chức năng**: Xem chi tiết một log kiểm kê
- **Serializer**: InventoryAuditLogSerializer
- **Quyền truy cập**: IsAdminUser (chỉ admin mới có thể truy cập)

## Quy trình quản lý kho hàng

1. **Thiết lập kho hàng**:
   - Admin tạo các kho hàng (Warehouse) để lưu trữ sản phẩm
   - Đánh dấu một kho hàng làm kho mặc định cho các sản phẩm mới

2. **Quản lý tồn kho**:
   - Khi tạo sản phẩm mới, hệ thống tự động tạo StockItem trong kho mặc định
   - Admin theo dõi và cập nhật số lượng tồn kho của từng sản phẩm trong từng kho
   - Thiết lập ngưỡng cảnh báo hàng tồn thấp để nhận thông báo khi cần nhập thêm hàng

3. **Xử lý di chuyển kho**:
   - Nhập kho (IN): Nhập thêm sản phẩm vào kho, tăng số lượng tồn kho
   - Xuất kho (OUT): Xuất sản phẩm ra khỏi kho, giảm số lượng tồn kho
   - Điều chỉnh (ADJUSTMENT): Điều chỉnh số lượng tồn kho do kiểm kê, hỏng hóc, mất mát, v.v.
   - Tự động liên kết với đơn hàng khi xuất kho do bán hàng

4. **Kiểm tra lịch sử và audit**:
   - Duy trì lịch sử đầy đủ của tất cả các thay đổi tồn kho
   - Ghi lại người thực hiện, thời gian, và lý do của mỗi thay đổi
   - Cung cấp khả năng truy xuất và báo cáo để kiểm toán

## Tính năng
- Tự động tạo StockItems khi sản phẩm mới được tạo
- Quản lý kho mặc định
- Ghi nhật ký chi tiết về các thay đổi tồn kho
- Lọc sản phẩm có tồn kho thấp hoặc hết hàng
- Tích hợp với app orders thông qua trường related_order

## Quy trình
1. Tạo kho hàng (Warehouse)
2. Khi tạo sản phẩm mới, StockItem được tự động tạo
3. Khi sản phẩm được đặt hàng, StockMovement OUT được tạo
4. Khi nhập hàng, StockMovement IN được tạo
5. Khi điều chỉnh tồn kho, StockMovement ADJUSTMENT được tạo
6. Tất cả thay đổi tồn kho được ghi lại trong InventoryAuditLog

## Tích hợp với các App khác
- **Products**: Theo dõi tồn kho cho sản phẩm
- **Orders**: Cập nhật tồn kho khi đơn hàng được tạo
- **Users**: Theo dõi người thực hiện các thay đổi
