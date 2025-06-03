from django.urls import path

app_name = 'catalog'

# Lưu ý: Tất cả đường dẫn trong catalog đã được di chuyển sang các URL riêng biệt:
# - api/v1/categories/
# - api/v1/brands/
# - api/v1/tags/
# - api/v1/attributes/
# - api/v1/attribute-values/

# Không còn sử dụng router với prefix /catalog/ nữa
urlpatterns = [
    # URLs đã được deprecated, không còn sử dụng nữa
]
