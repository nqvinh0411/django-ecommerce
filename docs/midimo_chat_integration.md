# Midimo Chat Integration Guide

## Tổng quan

Tài liệu này mô tả cách E-commerce kết nối với Midimo Chat thông qua gRPC API. Midimo Chat cung cấp các dịch vụ nhắn tin, quản lý trạng thái người dùng (presence) và thông báo.

## Cài đặt và thiết lập

### 1. Cài đặt dependencies

Thêm các dependencies sau vào `requirements.txt`:

```
grpcio==1.44.0
grpcio-tools==1.44.0
protobuf==3.20.0
PyJWT==2.4.0
```

Sau đó chạy:

```
pip install -r requirements.txt
```

### 2. Cấu hình kết nối

Cấu hình kết nối được định nghĩa trong file `settings/midimo_chat.py`. Cập nhật các thông số sau để phù hợp với môi trường của bạn:

```python
# Midimo Chat connection settings
MIDIMO_CHAT_HOST = "midimo-chat-service.example.com"  # Thay đổi theo môi trường
MIDIMO_CHAT_PORT = 50051  # Port mặc định cho gRPC
MIDIMO_CHAT_SECURE = True  # Sử dụng secure connection trong production

# JWT authentication
MIDIMO_CHAT_JWT_SECRET_KEY = "your-secret-key-here"  # Thay đổi trong production
```

### 3. Biên dịch Protobuf

Đặt các file `.proto` từ Midimo Chat vào thư mục `core/microservices/midimo_chat/protos/`:

```
core/
└── microservices/
    └── midimo_chat/
        └── protos/
            ├── chat.proto
            ├── presence.proto
            └── notification.proto
```

Sau đó, chạy lệnh sau để biên dịch:

```python
from core.microservices.midimo_chat.utils import generate_proto_files

generate_proto_files(
    proto_dir="/path/to/e_commerce/core/microservices/midimo_chat/protos"
)
```

Hoặc sử dụng lệnh protoc trực tiếp:

```bash
python -m grpc_tools.protoc \
    --proto_path=core/microservices/midimo_chat/protos \
    --python_out=core/microservices/midimo_chat/protos \
    --grpc_python_out=core/microservices/midimo_chat/protos \
    core/microservices/midimo_chat/protos/*.proto
```

## Kiến trúc kết nối

E-commerce giao tiếp với Midimo Chat thông qua ba lớp:

1. **MidimoChatClient** (`client.py`) - gRPC client trực tiếp, cung cấp các API cấp thấp
2. **Service wrappers** (`services.py`) - Các wrapper cấp cao cho tác vụ phổ biến
3. **Views/Endpoints** - Sử dụng các service wrapper để tích hợp với frontend

```
┌───────────────┐    ┌─────────────────┐    ┌─────────────┐
│ E-commerce    │    │ Midimo Chat     │    │ Frontend    │
│ Views/API     │    │ gRPC Service    │    │ Web/Mobile  │
└───────┬───────┘    └────────┬────────┘    └──────┬──────┘
        │                     │                    │
        │  ┌──────────────────┐                    │
        ├──┤ Service Wrappers │                    │
        │  └──────────────────┘                    │
        │                     │                    │
        │  ┌──────────────────┐                    │
        └──┤ gRPC Client      │                    │
           └──────────────────┘                    │
                     │                             │
                     └─────────────────────────────┘
                       WebSocket (direct connection)
```

## Sử dụng Client API

### Khởi tạo Client

```python
from core.microservices.midimo_chat.client import MidimoChatClient

# Khởi tạo với cấu hình mặc định từ settings
client = MidimoChatClient()

# Hoặc với cấu hình tùy chỉnh
client = MidimoChatClient(
    host="midimo-chat-service.example.com",
    port=50051,
    secure=True,
    timeout=5
)

# Sử dụng với context manager để tự động đóng kết nối
with MidimoChatClient() as client:
    # Use client here
    pass
```

### Tạo Chat Thread

```python
# Tạo thread chat mới
thread = client.create_thread(
    user_id="customer_123",
    title="Support Thread",
    participants=["support_agent_1"],
    metadata={
        "source": "e_commerce",
        "order_id": "order_456"
    }
)

thread_id = thread.id
```

### Gửi tin nhắn

```python
# Gửi tin nhắn đến thread
message = client.send_message(
    thread_id="thread_123",
    user_id="customer_123",
    content="Tôi muốn hỏi về đơn hàng của mình",
    attachment_ids=[]  # Optional attachment IDs
)
```

### Lấy tin nhắn

```python
# Lấy tin nhắn trong thread
messages = client.get_thread_messages(
    thread_id="thread_123",
    limit=50,
    before_id=None  # Optional, for pagination
)

for message in messages:
    print(f"{message.user_id}: {message.content}")
```

### Cập nhật trạng thái hiện diện

```python
# Cập nhật trạng thái người dùng
presence = client.update_presence(
    user_id="user_123",
    status="ONLINE",
    custom_status="Available for chat"
)
```

### Cập nhật trạng thái đang gõ

```python
# Bắt đầu gõ
client.update_typing_status(
    thread_id="thread_123",
    user_id="user_123",
    is_typing=True
)

# Dừng gõ
client.update_typing_status(
    thread_id="thread_123",
    user_id="user_123",
    is_typing=False
)
```

## Sử dụng Service Wrappers

Các service wrapper cung cấp API cấp cao hơn cho các tác vụ phổ biến.

### Chat Service

```python
from core.microservices.midimo_chat.services import ChatService

chat_service = ChatService()

# Tạo thread hỗ trợ khách hàng
thread = chat_service.create_support_thread(
    customer_id="customer_123",
    order_id="order_456",
    product_id="product_789"  # Optional
)

# Gửi cập nhật trạng thái đơn hàng qua chat
message = chat_service.send_order_update_message(
    thread_id="thread_123",
    order_id="order_456",
    status="Đã giao hàng",
    message="Đơn hàng của bạn đã được giao thành công!"
)
```

### Presence Service

```python
from core.microservices.midimo_chat.services import PresenceService

presence_service = PresenceService()

# Đặt trạng thái người dùng là online
presence_service.set_user_online(
    user_id="user_123",
    custom_status="Đang xem sản phẩm"
)

# Đặt trạng thái người dùng là offline
presence_service.set_user_offline(
    user_id="user_123"
)

# Kiểm tra tính khả dụng của các agent
availability = presence_service.get_agent_availability(
    agent_ids=["agent_1", "agent_2", "agent_3"]
)

# Bắt đầu/dừng gõ
presence_service.start_typing(
    thread_id="thread_123",
    user_id="user_123"
)

presence_service.stop_typing(
    thread_id="thread_123",
    user_id="user_123"
)
```

## Xử lý lỗi

Tất cả các API đều có cơ chế xử lý lỗi và retry. Các exception sau có thể được ném ra:

- `ServiceUnavailableError`: Midimo Chat service không khả dụng
- `ServiceTimeoutError`: Request timeout
- `AuthenticationError`: Lỗi xác thực
- `AuthorizationError`: Không có quyền thực hiện hành động
- `ValidationError`: Dữ liệu request không hợp lệ
- `ResourceNotFoundError`: Resource không tồn tại (ví dụ: thread không tồn tại)
- `ConflictError`: Xung đột dữ liệu

```python
from core.microservices.exceptions import ServiceUnavailableError

try:
    thread = client.create_thread(...)
except ServiceUnavailableError:
    # Xử lý khi service không khả dụng
    pass
except Exception as e:
    # Xử lý các lỗi khác
    pass
```

## Tích hợp vào API của E-commerce

Dưới đây là ví dụ về cách tích hợp Midimo Chat vào API của E-commerce:

```python
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

from core.microservices.midimo_chat.services import ChatService, PresenceService

@require_http_methods(["POST"])
def create_support_thread(request):
    """API endpoint để tạo thread hỗ trợ khách hàng"""
    data = json.loads(request.body)
    customer_id = data.get('customer_id')
    order_id = data.get('order_id')
    
    if not customer_id:
        return JsonResponse({'error': 'customer_id is required'}, status=400)
    
    try:
        chat_service = ChatService()
        thread = chat_service.create_support_thread(
            customer_id=customer_id,
            order_id=order_id
        )
        
        return JsonResponse({
            'thread_id': thread.id,
            'title': thread.title,
            'created_at': thread.created_at
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
```

## Giám sát và logging

Tất cả các API call đều được tự động logged với các thông tin như:
- Request ID
- Thời gian thực hiện
- Status code
- Error details (nếu có)

Bạn có thể theo dõi logs tại `logs/midimo_chat.log`.

## Best Practices

1. **Sử dụng context manager**: Luôn sử dụng `with` statement khi có thể để đảm bảo connection được đóng đúng cách.

2. **Cache kết quả**: Cache các kết quả không thay đổi thường xuyên như thread info.

3. **Rate limiting**: Tránh gọi API quá thường xuyên, đặc biệt là update_presence và update_typing.

4. **Error handling**: Luôn xử lý các exception để đảm bảo ứng dụng không bị crash.

5. **JWT token**: Bảo vệ JWT secret key và đảm bảo chỉ E-commerce mới có quyền truy cập.

## Troubleshooting

### Không thể kết nối đến Midimo Chat

Kiểm tra:
- Cấu hình `MIDIMO_CHAT_HOST` và `MIDIMO_CHAT_PORT`
- Firewall settings
- Network connectivity

### Authentication Errors

Kiểm tra:
- JWT secret key khớp giữa E-commerce và Midimo Chat
- JWT không hết hạn

### gRPC Errors

Nếu gặp lỗi về protobuf hoặc gRPC, đảm bảo:
- Các file protobuf đã được biên dịch đúng cách
- Phiên bản protobuf và gRPC libraries khớp với Midimo Chat

## Kết luận

Kết nối gRPC giữa E-commerce và Midimo Chat cho phép tích hợp chặt chẽ và hiệu quả giữa hai hệ thống. Với thiết kế modular và cơ chế xử lý lỗi mạnh mẽ, kết nối này cung cấp nền tảng vững chắc cho các tính năng chat trong E-commerce.
