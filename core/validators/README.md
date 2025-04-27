# Core Validators Module

## Giới thiệu
Module `validators` cung cấp các hàm validator tái sử dụng để xác thực dữ liệu đầu vào trong toàn bộ hệ thống e-commerce. Các validator này đảm bảo tính toàn vẹn và nhất quán của dữ liệu, giúp tránh các lỗi logic và bảo mật trong ứng dụng.

## Thành phần

### common.py
Định nghĩa các validator phổ biến có thể sử dụng trong serializers và form fields.

#### RegexValidators
- **`phone_regex`**: Kiểm tra định dạng số điện thoại
  - Định dạng: Bắt đầu tùy chọn với '+', theo sau là 9-15 chữ số
  - Ví dụ hợp lệ: '+84912345678', '0912345678'

- **`slug_regex`**: Kiểm tra định dạng slug
  - Định dạng: Chỉ chứa chữ thường, số và dấu gạch ngang
  - Ví dụ hợp lệ: 'my-product-slug', 'item123'

- **`email_regex`**: Kiểm tra định dạng email
  - Định dạng: Tuân theo chuẩn email thông thường
  - Ví dụ hợp lệ: 'user@example.com', 'name.surname@domain.co'

#### Validator Functions

##### `validate_slug(value)`
- **Mô tả**: Kiểm tra slug theo các quy tắc nâng cao:
  - Chỉ chứa chữ thường, số và dấu gạch ngang
  - Không bắt đầu hoặc kết thúc bằng dấu gạch ngang
  - Không chứa hai dấu gạch ngang liên tiếp
- **Ví dụ sử dụng**:
  ```python
  from core.validators.common import validate_slug
  
  class CategorySerializer(serializers.ModelSerializer):
      slug = serializers.SlugField(validators=[validate_slug])
      
      class Meta:
          model = Category
          fields = ['id', 'name', 'slug']
  ```

##### `validate_password(value)`
- **Mô tả**: Kiểm tra mật khẩu đủ mạnh:
  - Có ít nhất 8 ký tự
  - Có ít nhất một chữ số
  - Có ít nhất một chữ cái
  - Có ít nhất một chữ viết hoa
- **Ví dụ sử dụng**:
  ```python
  from core.validators.common import validate_password
  
  class RegisterSerializer(serializers.ModelSerializer):
      password = serializers.CharField(
          validators=[validate_password],
          style={'input_type': 'password'}
      )
  ```

## Cách sử dụng
Validator có thể được sử dụng ở nhiều nơi trong Django:

### Trong Serializers
```python
from core.validators.common import phone_regex, validate_password

class UserProfileSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(validators=[phone_regex])
    password = serializers.CharField(
        validators=[validate_password], 
        write_only=True
    )
    
    class Meta:
        model = UserProfile
        fields = ['id', 'phone_number', 'password']
```

### Trong Model Fields
```python
from django.db import models
from core.validators.common import phone_regex

class Customer(models.Model):
    phone_number = models.CharField(
        max_length=15, 
        validators=[phone_regex],
        blank=True
    )
```

### Trong Form Fields
```python
from django import forms
from core.validators.common import validate_password

class PasswordResetForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput(),
        validators=[validate_password]
    )
```

## Mở rộng
Module validators có thể mở rộng để hỗ trợ:
- Validators cho định dạng hình ảnh và tệp
- Validators kiểm tra kích thước và nội dung tệp
- Validators cho dữ liệu đặc thù ngành như mã sản phẩm, mã giảm giá, etc.
