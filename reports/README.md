# Reports App

## Mô tả
App `reports` cung cấp các báo cáo, phân tích và thống kê về hoạt động kinh doanh trong hệ thống e-commerce. App này giúp quản trị viên và nhà quản lý có cái nhìn tổng quan về hiệu suất bán hàng, hành vi người dùng, và xu hướng kinh doanh.

## Mô hình dữ liệu

### ReportConfiguration
Cấu hình báo cáo:
- `name`: Tên báo cáo
- `description`: Mô tả báo cáo
- `report_type`: Loại báo cáo (SALES, INVENTORY, CUSTOMER, MARKETING)
- `query`: Truy vấn SQL hoặc cấu hình báo cáo
- `schedule`: Lịch trình tự động (DAILY, WEEKLY, MONTHLY, QUARTERLY)
- `recipients`: Danh sách người nhận báo cáo
- `last_run`: Lần chạy gần nhất
- `created_by`: Người tạo báo cáo
- `created_at`: Thời điểm tạo
- `updated_at`: Thời điểm cập nhật

### ReportData
Dữ liệu báo cáo đã tạo:
- `report_config`: Liên kết đến ReportConfiguration
- `data_json`: Dữ liệu báo cáo dạng JSON
- `generated_at`: Thời điểm tạo báo cáo
- `file_path`: Đường dẫn đến file báo cáo (nếu có)

### SalesReport
Thông tin báo cáo doanh số:
- `start_date`: Ngày bắt đầu
- `end_date`: Ngày kết thúc
- `total_sales`: Tổng doanh số
- `total_orders`: Tổng số đơn hàng
- `average_order_value`: Giá trị đơn hàng trung bình
- `top_products`: Sản phẩm bán chạy
- `top_categories`: Danh mục bán chạy
- `generated_at`: Thời điểm tạo báo cáo

### InventoryReport
Báo cáo tồn kho:
- `generated_at`: Thời điểm tạo báo cáo
- `total_products`: Tổng số sản phẩm
- `total_stock_value`: Tổng giá trị tồn kho
- `low_stock_items`: Các mặt hàng tồn kho thấp
- `out_of_stock_items`: Các mặt hàng hết hàng
- `slow_moving_items`: Các mặt hàng bán chậm

### Analytics
Dữ liệu phân tích:
- `date`: Ngày phân tích
- `metric_type`: Loại chỉ số (PAGE_VIEW, CONVERSION, CART_ABANDONMENT, etc.)
- `metric_value`: Giá trị chỉ số
- `dimension`: Chiều đo (PRODUCT, CATEGORY, USER_TYPE, etc.)
- `dimension_value`: Giá trị chiều đo

## API Endpoints
- Tạo báo cáo tùy chỉnh
- Xem báo cáo doanh số
- Xem báo cáo tồn kho
- Xem báo cáo khách hàng
- Phân tích xu hướng

## Tính năng
- Dashboard tổng quan cho quản trị viên
- Báo cáo doanh số theo thời gian thực
- Phân tích hành vi người dùng
- Báo cáo tồn kho và cảnh báo
- Phân tích ROI cho các chiến dịch marketing
- Xuất báo cáo dưới nhiều định dạng (PDF, Excel, CSV)
- Lên lịch tự động gửi báo cáo

## Biểu đồ và Trực quan hóa
- Biểu đồ doanh số theo thời gian
- Biểu đồ phân bố danh mục sản phẩm
- Heatmap hoạt động người dùng
- Funnel chuyển đổi
- So sánh hiệu suất

## Tích hợp với các App khác
- **Orders**: Dữ liệu doanh số và đơn hàng
- **Products**: Dữ liệu sản phẩm bán chạy
- **Customers**: Phân tích hành vi và phân khúc khách hàng
- **Inventory**: Dữ liệu tồn kho
- **Marketing**: Hiệu quả chiến dịch marketing
- **Users**: Phân tích hoạt động của người dùng
- **Promotions**: Đánh giá hiệu quả khuyến mãi
