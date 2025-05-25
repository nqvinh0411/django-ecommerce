"""
Midimo Chat Webhook Handlers.

Module này cung cấp các handlers để xử lý webhooks từ Midimo Chat Service,
đảm bảo tuân thủ tiêu chuẩn API trong việc tích hợp giữa các dịch vụ.
"""

import hmac
import hashlib
import json
import logging
from functools import wraps
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings

from core.utils.response import success_response, error_response

logger = logging.getLogger('midimo_chat_webhooks')

# Định nghĩa các loại sự kiện được hỗ trợ
SUPPORTED_EVENTS = {
    'message.created': 'Tin nhắn mới được tạo',
    'message.updated': 'Tin nhắn được cập nhật',
    'message.deleted': 'Tin nhắn bị xóa',
    'conversation.created': 'Cuộc trò chuyện mới được tạo',
    'conversation.updated': 'Cuộc trò chuyện được cập nhật',
    'conversation.deleted': 'Cuộc trò chuyện bị xóa',
    'user.presence_changed': 'Trạng thái hiện diện của người dùng thay đổi',
    'user.typing': 'Người dùng đang nhập tin nhắn',
}


def verify_webhook_signature(webhook_secret):
    """
    Decorator để xác thực webhook signature.
    
    Args:
        webhook_secret (str): Secret key để xác thực webhook
        
    Returns:
        function: Decorated view function
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Lấy signature từ header
            signature = request.headers.get('X-Midimo-Signature')
            if not signature:
                logger.warning("Missing X-Midimo-Signature header in webhook request")
                return error_response(
                    message="Missing signature header",
                    status_code=401
                )
                
            # Tính toán signature từ request body
            request_body = request.body
            expected_signature = hmac.new(
                webhook_secret.encode(),
                request_body,
                hashlib.sha256
            ).hexdigest()
            
            # So sánh signatures
            if not hmac.compare_digest(signature, expected_signature):
                logger.warning("Invalid webhook signature")
                return error_response(
                    message="Invalid webhook signature",
                    status_code=401
                )
                
            # Signature hợp lệ, tiếp tục xử lý request
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


@csrf_exempt
@require_POST
@verify_webhook_signature(getattr(settings, 'MIDIMO_CHAT_WEBHOOK_SECRET', ''))
def webhook_handler(request):
    """
    Handler chính cho tất cả webhooks từ Midimo Chat.
    
    Args:
        request: Django HttpRequest
        
    Returns:
        JsonResponse: Response với định dạng chuẩn
    """
    try:
        # Parse request body
        payload = json.loads(request.body)
        
        # Lấy event_type từ payload
        event_type = payload.get('event_type')
        if not event_type:
            logger.error("Missing event_type in webhook payload")
            return error_response(
                message="Missing event_type in payload",
                status_code=400
            )
            
        # Kiểm tra xem event_type có được hỗ trợ không
        if event_type not in SUPPORTED_EVENTS:
            logger.warning(f"Unsupported event_type: {event_type}")
            return error_response(
                message=f"Unsupported event_type: {event_type}",
                status_code=400
            )
            
        # Dispatch event đến handler tương ứng
        logger.info(f"Received webhook event: {event_type}")
        
        # Xử lý các loại sự kiện khác nhau
        if event_type.startswith('message.'):
            return handle_message_event(event_type, payload)
        elif event_type.startswith('conversation.'):
            return handle_conversation_event(event_type, payload)
        elif event_type.startswith('user.'):
            return handle_user_event(event_type, payload)
        else:
            # Fallback cho các sự kiện khác
            logger.info(f"Using default handler for event: {event_type}")
            return handle_default_event(event_type, payload)
            
    except json.JSONDecodeError:
        logger.error("Invalid JSON payload in webhook request")
        return error_response(
            message="Invalid JSON payload",
            status_code=400
        )
    except Exception as e:
        logger.exception(f"Error processing webhook: {str(e)}")
        return error_response(
            message=f"Error processing webhook: {str(e)}",
            status_code=500
        )


def handle_message_event(event_type, payload):
    """
    Xử lý sự kiện liên quan đến tin nhắn.
    
    Args:
        event_type (str): Loại sự kiện
        payload (dict): Dữ liệu sự kiện
        
    Returns:
        JsonResponse: Response với định dạng chuẩn
    """
    # Lấy dữ liệu từ payload
    message_data = payload.get('data', {})
    conversation_id = message_data.get('conversation_id')
    message_id = message_data.get('id')
    user_id = message_data.get('user_id')
    
    # Log sự kiện
    logger.info(
        f"Processing {event_type} event - Message ID: {message_id}, "
        f"Conversation ID: {conversation_id}, User ID: {user_id}"
    )
    
    # Thực hiện các hành động dựa trên loại sự kiện
    if event_type == 'message.created':
        # Xử lý sự kiện tin nhắn mới
        # TODO: Thêm logic xử lý sự kiện tin nhắn mới
        pass
    elif event_type == 'message.updated':
        # Xử lý sự kiện tin nhắn được cập nhật
        # TODO: Thêm logic xử lý sự kiện tin nhắn được cập nhật
        pass
    elif event_type == 'message.deleted':
        # Xử lý sự kiện tin nhắn bị xóa
        # TODO: Thêm logic xử lý sự kiện tin nhắn bị xóa
        pass
    
    # Trả về response thành công
    return success_response(
        message=f"Successfully processed {event_type} event",
        status_code=200
    )


def handle_conversation_event(event_type, payload):
    """
    Xử lý sự kiện liên quan đến cuộc trò chuyện.
    
    Args:
        event_type (str): Loại sự kiện
        payload (dict): Dữ liệu sự kiện
        
    Returns:
        JsonResponse: Response với định dạng chuẩn
    """
    # Lấy dữ liệu từ payload
    conversation_data = payload.get('data', {})
    conversation_id = conversation_data.get('id')
    
    # Log sự kiện
    logger.info(f"Processing {event_type} event - Conversation ID: {conversation_id}")
    
    # Thực hiện các hành động dựa trên loại sự kiện
    if event_type == 'conversation.created':
        # Xử lý sự kiện cuộc trò chuyện mới
        # TODO: Thêm logic xử lý sự kiện cuộc trò chuyện mới
        pass
    elif event_type == 'conversation.updated':
        # Xử lý sự kiện cuộc trò chuyện được cập nhật
        # TODO: Thêm logic xử lý sự kiện cuộc trò chuyện được cập nhật
        pass
    elif event_type == 'conversation.deleted':
        # Xử lý sự kiện cuộc trò chuyện bị xóa
        # TODO: Thêm logic xử lý sự kiện cuộc trò chuyện bị xóa
        pass
    
    # Trả về response thành công
    return success_response(
        message=f"Successfully processed {event_type} event",
        status_code=200
    )


def handle_user_event(event_type, payload):
    """
    Xử lý sự kiện liên quan đến người dùng.
    
    Args:
        event_type (str): Loại sự kiện
        payload (dict): Dữ liệu sự kiện
        
    Returns:
        JsonResponse: Response với định dạng chuẩn
    """
    # Lấy dữ liệu từ payload
    user_data = payload.get('data', {})
    user_id = user_data.get('user_id')
    
    # Log sự kiện
    logger.info(f"Processing {event_type} event - User ID: {user_id}")
    
    # Thực hiện các hành động dựa trên loại sự kiện
    if event_type == 'user.presence_changed':
        # Xử lý sự kiện thay đổi trạng thái hiện diện
        # TODO: Thêm logic xử lý sự kiện thay đổi trạng thái hiện diện
        status = user_data.get('status')
        logger.info(f"User {user_id} changed presence status to {status}")
        pass
    elif event_type == 'user.typing':
        # Xử lý sự kiện người dùng đang nhập tin nhắn
        # TODO: Thêm logic xử lý sự kiện người dùng đang nhập tin nhắn
        conversation_id = user_data.get('conversation_id')
        logger.info(f"User {user_id} is typing in conversation {conversation_id}")
        pass
    
    # Trả về response thành công
    return success_response(
        message=f"Successfully processed {event_type} event",
        status_code=200
    )


def handle_default_event(event_type, payload):
    """
    Xử lý các loại sự kiện không có handler riêng.
    
    Args:
        event_type (str): Loại sự kiện
        payload (dict): Dữ liệu sự kiện
        
    Returns:
        JsonResponse: Response với định dạng chuẩn
    """
    # Log sự kiện
    logger.info(f"Processing default handler for event: {event_type}")
    
    # Trả về response thành công
    return success_response(
        message=f"Acknowledged {event_type} event",
        status_code=200
    )
