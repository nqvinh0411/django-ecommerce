# Core Authentication Module

## Giới thiệu
Module `authentication` cung cấp các tiện ích cho việc xác thực và quản lý JWT tokens trong hệ thống e-commerce.

## Thành phần

### tokens.py
Cung cấp các hàm tiện ích để làm việc với JWT tokens.

#### `get_tokens_for_user(user)`
- **Mô tả**: Tạo JWT tokens (access và refresh) cho người dùng
- **Tham số**: `user` - Đối tượng User cần tạo token
- **Trả về**: Dictionary chứa access_token và refresh_token
- **Ví dụ sử dụng**:
  ```python
  from core.authentication.tokens import get_tokens_for_user
  
  tokens = get_tokens_for_user(user)
  # Kết quả: {'refresh': 'token...', 'access': 'token...'}
  ```

#### `configure_token_settings()`
- **Mô tả**: Cấu hình mặc định cho JWT tokens, dùng trong settings.py
- **Trả về**: Dictionary cấu hình cho SIMPLE_JWT setting
- **Ví dụ sử dụng**:
  ```python
  # Trong settings.py
  from core.authentication.tokens import configure_token_settings
  
  SIMPLE_JWT = configure_token_settings()
  ```

## Tích hợp
Module này tích hợp chặt chẽ với `rest_framework_simplejwt` và được sử dụng làm nền tảng cho hệ thống xác thực trong project.

## Cách mở rộng
Có thể thêm các custom authentication backends vào module này để mở rộng khả năng xác thực theo nhu cầu cụ thể, ví dụ:
- Email authentication
- Social authentication
- Two-factor authentication
