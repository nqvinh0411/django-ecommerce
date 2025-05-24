"""
Midimo Chat gRPC client
"""

import logging
import grpc
from django.conf import settings

from ..base import BaseMicroserviceClient
from ..middleware import AuthInterceptor, MetricsInterceptor
from ..auth import get_default_token_provider

# Import gRPC generated modules
# These would be generated from the proto files provided by Midimo Chat
try:
    from .protos import chat_pb2, chat_pb2_grpc
    from .protos import presence_pb2, presence_pb2_grpc
except ImportError:
    # Log warning - actual implementation should handle this more gracefully
    logging.warning("Midimo Chat gRPC protos not found. You need to generate them first.")


class MidimoChatClient(BaseMicroserviceClient):
    """
    Client for interacting with Midimo Chat service via gRPC
    """
    
    def __init__(self, host=None, port=None, secure=False, timeout=10):
        """
        Initialize the Midimo Chat client
        
        Args:
            host: Midimo Chat host (defaults to settings.MIDIMO_CHAT_HOST)
            port: Midimo Chat port (defaults to settings.MIDIMO_CHAT_PORT)
            secure: Whether to use a secure connection
            timeout: Default timeout in seconds
        """
        # Initialize base client
        super().__init__(
            service_name="midimo_chat",
            host=host,
            port=port,
            secure=secure,
            timeout=timeout
        )
        
        # Initialize stubs for different services
        self._chat_stub = chat_pb2_grpc.ChatServiceStub(self.channel)
        self._presence_stub = presence_pb2_grpc.PresenceServiceStub(self.channel)
        
        # Log successful initialization
        logging.info(f"Midimo Chat client initialized with host={self.host}, port={self.port}")
    
    def _get_interceptors(self):
        """Get channel interceptors for Midimo Chat"""
        # Get token provider for Midimo Chat service
        token_provider = get_default_token_provider(service_name="midimo_chat")
        
        return [
            AuthInterceptor(token_provider),
            MetricsInterceptor(service_name="midimo_chat")
        ]
    
    # Chat methods
    
    def create_thread(self, user_id, title=None, participants=None, metadata=None):
        """
        Create a new chat thread
        
        Args:
            user_id: ID of the user creating the thread
            title: Optional title for the thread
            participants: List of participant user IDs (besides the creator)
            metadata: Optional metadata for the thread (dict)
        
        Returns:
            Thread object
        """
        # Create request
        request = chat_pb2.CreateThreadRequest(
            user_id=user_id,
            title=title or "",
            participants=participants or [],
            metadata=metadata or {}
        )
        
        # Call gRPC method with retry
        response = self._call_with_retry(
            self._chat_stub.CreateThread,
            request
        )
        
        return response.thread
    
    def send_message(self, thread_id, user_id, content, attachment_ids=None):
        """
        Send a message to a thread
        
        Args:
            thread_id: ID of the thread
            user_id: ID of the user sending the message
            content: Message content
            attachment_ids: Optional list of attachment IDs
        
        Returns:
            Message object
        """
        # Create request
        request = chat_pb2.SendMessageRequest(
            thread_id=thread_id,
            user_id=user_id,
            content=content,
            attachment_ids=attachment_ids or []
        )
        
        # Call gRPC method with retry
        response = self._call_with_retry(
            self._chat_stub.SendMessage,
            request
        )
        
        return response.message
    
    def get_thread_messages(self, thread_id, limit=50, before_id=None):
        """
        Get messages from a thread
        
        Args:
            thread_id: ID of the thread
            limit: Maximum number of messages to return
            before_id: Only return messages before this ID
        
        Returns:
            List of Message objects
        """
        # Create request
        request = chat_pb2.GetThreadMessagesRequest(
            thread_id=thread_id,
            limit=limit,
            before_id=before_id or ""
        )
        
        # Call gRPC method with retry
        response = self._call_with_retry(
            self._chat_stub.GetThreadMessages,
            request
        )
        
        return response.messages
    
    # Presence methods
    
    def update_presence(self, user_id, status, custom_status=None):
        """
        Update a user's presence status
        
        Args:
            user_id: ID of the user
            status: Presence status (online, away, offline)
            custom_status: Optional custom status message
        
        Returns:
            PresenceData object
        """
        # Create request
        request = presence_pb2.UpdatePresenceRequest(
            user_id=user_id,
            status=status,
            custom_status=custom_status or ""
        )
        
        # Call gRPC method with retry
        response = self._call_with_retry(
            self._presence_stub.UpdatePresence,
            request
        )
        
        return response.presence
    
    def get_presence(self, user_ids):
        """
        Get presence status for multiple users
        
        Args:
            user_ids: List of user IDs
        
        Returns:
            Dict mapping user_id to PresenceData
        """
        # Create request
        request = presence_pb2.GetPresenceRequest(
            user_ids=user_ids
        )
        
        # Call gRPC method with retry
        response = self._call_with_retry(
            self._presence_stub.GetPresence,
            request
        )
        
        return {p.user_id: p for p in response.presence_data}
    
    def update_typing_status(self, thread_id, user_id, is_typing):
        """
        Update typing status in a thread
        
        Args:
            thread_id: ID of the thread
            user_id: ID of the user
            is_typing: Whether the user is typing
        """
        # Create request
        request = presence_pb2.TypingRequest(
            thread_id=thread_id,
            user_id=user_id,
            is_typing=is_typing
        )
        
        # Call gRPC method with retry
        self._call_with_retry(
            self._presence_stub.UpdateTyping,
            request
        )
