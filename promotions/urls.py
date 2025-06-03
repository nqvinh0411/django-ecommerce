from django.urls import path

app_name = 'promotions'

# Lưu ý: Tất cả đường dẫn trong promotions đã được di chuyển sang các URL riêng biệt:
# - api/v1/coupons/
# - api/v1/vouchers/
# - api/v1/campaigns/
# - api/v1/usage-logs/

# Không còn sử dụng router với prefix /promotions/ nữa
urlpatterns = [
    # URLs đã được deprecated, không còn sử dụng nữa
]
