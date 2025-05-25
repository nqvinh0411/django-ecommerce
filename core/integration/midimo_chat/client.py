"""
Midimo Chat Integration Client.

Module này cung cấp client để tích hợp với Midimo Chat Service,
đảm bảo tuân thủ các chuẩn API đã định nghĩa trong tài liệu.
"""

import os
import json
import logging
import requests
from django.conf import settings
import grpc
from google.protobuf.json_format import MessageToDict

# Thiết lập logger
logger = logging.getLogger('midimo_chat_integration')


class MidimoChatClientError(Exception):
    """Exception cơ sở cho các lỗi trong Midimo Chat Client."""
    pass


class ConnectionError(MidimoChatClientError):
    """Lỗi kết nối đến Midimo Chat Service."""
    pass


class AuthenticationError(MidimoChatClientError):
    """Lỗi xác thực với Midimo Chat Service."""
    pass


class ApiError(MidimoChatClientError):
    """Lỗi API từ Midimo Chat Service."""
    def __init__(self, status_code, message, errors=None):
        self.status_code = status_code
        self.errors = errors
        super().__init__(message)


class MidimoChatRESTClient:
    """
    Client cho REST API của Midimo Chat Service.
    
    Client này đảm bảo rằng mọi request đến Midimo Chat REST API
    đều tuân thủ định dạng và tiêu chuẩn đã định nghĩa.
    
    Attributes:
        base_url (str): URL cơ sở của Midimo Chat API
        api_key (str): API key để xác thực với Midimo Chat
        timeout (int): Thời gian timeout cho mỗi request (giây)
        use_ssl (bool): Có sử dụng SSL không
    """
    
    def __init__(self, api_key=None, timeout=10):
        """
        Khởi tạo REST client.
        
        Args:
            api_key (str, optional): API key. Nếu None, sẽ lấy từ settings.
            timeout (int, optional): Thời gian timeout. Mặc định: 10.
        """
        self.api_key = api_key or getattr(settings, 'MIDIMO_CHAT_API_KEY', '')
        self.timeout = timeout
        self.use_ssl = getattr(settings, 'MIDIMO_CHAT_USE_SSL', True)
        
        # Lấy host và port từ settings
        host = getattr(settings, 'MIDIMO_CHAT_HOST', 'localhost')
        port = getattr(settings, 'MIDIMO_CHAT_PORT', 8000)
        
        # Tạo base URL
        protocol = 'https' if self.use_ssl else 'http'
        self.base_url = f"{protocol}://{host}:{port}/api/v1"
        
        logger.info(f"Initialized Midimo Chat REST client with base URL: {self.base_url}")
    
    def _get_headers(self):
        """
        Tạo headers cho request.
        
        Returns:
            dict: Headers cho request
        """
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-API-KEY': self.api_key
        }
    
    def _handle_response(self, response):
        """
        Xử lý response từ API.
        
        Args:
            response: Response object từ requests
            
        Returns:
            dict: Dữ liệu response đã được xử lý
            
        Raises:
            ConnectionError: Nếu có lỗi kết nối
            AuthenticationError: Nếu có lỗi xác thực
            ApiError: Nếu có lỗi API khác
        """
        try:
            # Parse JSON response
            data = response.json()
            
            # Kiểm tra nếu response là lỗi
            if response.status_code >= 400 or data.get('status') == 'error':
                message = data.get('message', 'Unknown API error')
                errors = data.get('errors')
                
                if response.status_code == 401:
                    raise AuthenticationError(message)
                else:
                    raise ApiError(response.status_code, message, errors)
            
            # Trả về data nếu success
            return data.get('data', {})
            
        except ValueError:
            # Lỗi parse JSON
            logger.error(f"Invalid JSON response: {response.text}")
            raise ApiError(
                response.status_code,
                "Invalid response format from Midimo Chat API"
            )
    
    def request(self, method, endpoint, data=None, params=None):
        """
        Thực hiện request đến Midimo Chat API.
        
        Args:
            method (str): HTTP method (GET, POST, etc.)
            endpoint (str): API endpoint
            data (dict, optional): Request body. Mặc định: None.
            params (dict, optional): Query parameters. Mặc định: None.
            
        Returns:
            dict: Dữ liệu response đã được xử lý
            
        Raises:
            ConnectionError: Nếu có lỗi kết nối
            AuthenticationError: Nếu có lỗi xác thực
            ApiError: Nếu có lỗi API khác
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        
        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            return self._handle_response(response)
            
        except requests.RequestException as e:
            logger.error(f"Connection error to Midimo Chat API: {str(e)}")
            raise ConnectionError(f"Failed to connect to Midimo Chat API: {str(e)}")
    
    # Các phương thức tiện ích cho từng endpoint
    
    def get_user_presence(self, user_id):
        """
        Lấy trạng thái hiện diện của user.
        
        Args:
            user_id (str): ID của user
            
        Returns:
            dict: Thông tin hiện diện của user
        """
        return self.request('GET', f'/users/{user_id}/presence')
    
    def update_user_presence(self, user_id, status, custom_message=None):
        """
        Cập nhật trạng thái hiện diện của user.
        
        Args:
            user_id (str): ID của user
            status (str): Trạng thái hiện diện (online, away, busy, offline)
            custom_message (str, optional): Tin nhắn tùy chỉnh. Mặc định: None.
            
        Returns:
            dict: Thông tin hiện diện đã cập nhật
        """
        data = {
            'status': status
        }
        if custom_message:
            data['custom_message'] = custom_message
            
        return self.request('PUT', f'/users/{user_id}/presence', data=data)
    
    def get_user_conversations(self, user_id, page=1, limit=20):
        """
        Lấy danh sách cuộc trò chuyện của user.
        
        Args:
            user_id (str): ID của user
            page (int, optional): Số trang. Mặc định: 1.
            limit (int, optional): Số cuộc trò chuyện mỗi trang. Mặc định: 20.
            
        Returns:
            dict: Danh sách cuộc trò chuyện
        """
        params = {
            'page': page,
            'limit': limit
        }
        return self.request('GET', f'/users/{user_id}/conversations', params=params)
    
    def create_conversation(self, participants, title=None, metadata=None):
        """
        Tạo cuộc trò chuyện mới.
        
        Args:
            participants (list): Danh sách ID của người tham gia
            title (str, optional): Tiêu đề cuộc trò chuyện. Mặc định: None.
            metadata (dict, optional): Metadata cho cuộc trò chuyện. Mặc định: None.
            
        Returns:
            dict: Thông tin cuộc trò chuyện mới
        """
        data = {
            'participants': participants
        }
        if title:
            data['title'] = title
        if metadata:
            data['metadata'] = metadata
            
        return self.request('POST', '/conversations', data=data)
    
    def send_message(self, conversation_id, user_id, content, content_type='text', metadata=None):
        """
        Gửi tin nhắn trong cuộc trò chuyện.
        
        Args:
            conversation_id (str): ID của cuộc trò chuyện
            user_id (str): ID của người gửi
            content (str): Nội dung tin nhắn
            content_type (str, optional): Loại nội dung. Mặc định: 'text'.
            metadata (dict, optional): Metadata cho tin nhắn. Mặc định: None.
            
        Returns:
            dict: Thông tin tin nhắn đã gửi
        """
        data = {
            'user_id': user_id,
            'content': content,
            'content_type': content_type
        }
        if metadata:
            data['metadata'] = metadata
            
        return self.request('POST', f'/conversations/{conversation_id}/messages', data=data)


class MidimoChatGRPCClient:
    """
    Client cho gRPC API của Midimo Chat Service.
    
    Client này đảm bảo rằng mọi request đến Midimo Chat gRPC API
    đều tuân thủ định dạng và tiêu chuẩn đã định nghĩa.
    
    Attributes:
        channel: gRPC channel
        stub_chat: Chat service stub
        stub_presence: Presence service stub
    """
    
    def __init__(self):
        """
        Khởi tạo gRPC client.
        """
        # Import các generated stubs từ proto
        # Trong trường hợp thực tế, cần sử dụng proto đã được compile
        try:
            from midimo_chat.grpc import chat_pb2, chat_pb2_grpc
            from midimo_chat.grpc import presence_pb2, presence_pb2_grpc
            
            # Lấy host và port từ settings
            host = getattr(settings, 'MIDIMO_CHAT_GRPC_HOST', 'localhost')
            port = getattr(settings, 'MIDIMO_CHAT_GRPC_PORT', 50051)
            
            # Tạo secure channel nếu cần
            use_ssl = getattr(settings, 'MIDIMO_CHAT_GRPC_USE_SSL', False)
            if use_ssl:
                creds = grpc.ssl_channel_credentials()
                self.channel = grpc.secure_channel(f"{host}:{port}", creds)
            else:
                self.channel = grpc.insecure_channel(f"{host}:{port}")
            
            # Tạo stubs
            self.stub_chat = chat_pb2_grpc.ChatServiceStub(self.channel)
            self.stub_presence = presence_pb2_grpc.PresenceServiceStub(self.channel)
            
            # Lưu classes để tạo messages
            self.chat_pb2 = chat_pb2
            self.presence_pb2 = presence_pb2
            
            logger.info(f"Initialized Midimo Chat gRPC client with server: {host}:{port}")
            
        except ImportError as e:
            logger.error(f"Failed to import gRPC stubs: {str(e)}")
            raise ImportError(f"Failed to load gRPC stubs. Make sure proto files are compiled: {str(e)}")
    
    def update_presence(self, user_id, status, device_id=None, custom_message=None):
        """
        Cập nhật trạng thái hiện diện của user.
        
        Args:
            user_id (str): ID của user
            status (str): Trạng thái hiện diện (ONLINE, AWAY, BUSY, OFFLINE)
            device_id (str, optional): ID của thiết bị. Mặc định: None.
            custom_message (str, optional): Tin nhắn tùy chỉnh. Mặc định: None.
            
        Returns:
            dict: Thông tin hiện diện đã cập nhật
        """
        try:
            # Tạo request message
            request = self.presence_pb2.UpdatePresenceRequest(
                user_id=user_id,
                status=status
            )
            
            if device_id:
                request.device_id = device_id
            if custom_message:
                request.custom_message = custom_message
            
            # Gọi gRPC method
            response = self.stub_presence.UpdatePresence(request)
            
            # Convert protobuf message sang dict
            return MessageToDict(
                response,
                preserving_proto_field_name=True,
                including_default_value_fields=True
            )
            
        except grpc.RpcError as e:
            status_code = e.code()
            detail = e.details()
            logger.error(f"gRPC error ({status_code}): {detail}")
            
            if status_code == grpc.StatusCode.UNAUTHENTICATED:
                raise AuthenticationError(detail)
            elif status_code == grpc.StatusCode.UNAVAILABLE:
                raise ConnectionError(f"gRPC service unavailable: {detail}")
            else:
                raise ApiError(status_code.value[0], detail)
    
    def get_presence(self, user_id):
        """
        Lấy trạng thái hiện diện của user.
        
        Args:
            user_id (str): ID của user
            
        Returns:
            dict: Thông tin hiện diện của user
        """
        try:
            # Tạo request message
            request = self.presence_pb2.GetPresenceRequest(user_id=user_id)
            
            # Gọi gRPC method
            response = self.stub_presence.GetPresence(request)
            
            # Convert protobuf message sang dict
            return MessageToDict(
                response,
                preserving_proto_field_name=True,
                including_default_value_fields=True
            )
            
        except grpc.RpcError as e:
            status_code = e.code()
            detail = e.details()
            logger.error(f"gRPC error ({status_code}): {detail}")
            
            if status_code == grpc.StatusCode.UNAUTHENTICATED:
                raise AuthenticationError(detail)
            elif status_code == grpc.StatusCode.UNAVAILABLE:
                raise ConnectionError(f"gRPC service unavailable: {detail}")
            else:
                raise ApiError(status_code.value[0], detail)
    
    def send_message(self, conversation_id, user_id, content, content_type='TEXT'):
        """
        Gửi tin nhắn trong cuộc trò chuyện.
        
        Args:
            conversation_id (str): ID của cuộc trò chuyện
            user_id (str): ID của người gửi
            content (str): Nội dung tin nhắn
            content_type (str, optional): Loại nội dung. Mặc định: 'TEXT'.
            
        Returns:
            dict: Thông tin tin nhắn đã gửi
        """
        try:
            # Tạo request message
            request = self.chat_pb2.SendMessageRequest(
                conversation_id=conversation_id,
                user_id=user_id,
                content=content,
                content_type=content_type
            )
            
            # Gọi gRPC method
            response = self.stub_chat.SendMessage(request)
            
            # Convert protobuf message sang dict
            return MessageToDict(
                response,
                preserving_proto_field_name=True,
                including_default_value_fields=True
            )
            
        except grpc.RpcError as e:
            status_code = e.code()
            detail = e.details()
            logger.error(f"gRPC error ({status_code}): {detail}")
            
            if status_code == grpc.StatusCode.UNAUTHENTICATED:
                raise AuthenticationError(detail)
            elif status_code == grpc.StatusCode.UNAVAILABLE:
                raise ConnectionError(f"gRPC service unavailable: {detail}")
            else:
                raise ApiError(status_code.value[0], detail)
    
    def close(self):
        """
        Đóng gRPC channel.
        """
        if hasattr(self, 'channel'):
            self.channel.close()


# Tạo instance mặc định để sử dụng trong ứng dụng
default_rest_client = None
default_grpc_client = None

def get_rest_client():
    """
    Lấy instance mặc định của REST client.
    
    Returns:
        MidimoChatRESTClient: Instance của REST client
    """
    global default_rest_client
    if default_rest_client is None:
        default_rest_client = MidimoChatRESTClient()
    return default_rest_client

def get_grpc_client():
    """
    Lấy instance mặc định của gRPC client.
    
    Returns:
        MidimoChatGRPCClient: Instance của gRPC client
    """
    global default_grpc_client
    if default_grpc_client is None:
        default_grpc_client = MidimoChatGRPCClient()
    return default_grpc_client
