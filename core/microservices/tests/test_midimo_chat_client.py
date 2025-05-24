"""
Tests for Midimo Chat gRPC client
"""

import unittest
from unittest import mock
import grpc
from django.test import TestCase
from django.conf import settings

from ..midimo_chat.client import MidimoChatClient
from ..exceptions import ServiceUnavailableError, ServiceTimeoutError


class MidimoChatClientTests(TestCase):
    """Test cases for MidimoChatClient"""
    
    @mock.patch('grpc.insecure_channel')
    def setUp(self, mock_insecure_channel):
        """Set up test environment"""
        # Mock the gRPC channel
        self.mock_channel = mock.MagicMock()
        mock_insecure_channel.return_value = self.mock_channel
        
        # Mock the gRPC stubs
        self.mock_chat_stub = mock.MagicMock()
        self.mock_presence_stub = mock.MagicMock()
        
        # Create client with mocked components
        with mock.patch('core.microservices.midimo_chat.client.chat_pb2_grpc') as mock_chat_grpc:
            with mock.patch('core.microservices.midimo_chat.client.presence_pb2_grpc') as mock_presence_grpc:
                mock_chat_grpc.ChatServiceStub.return_value = self.mock_chat_stub
                mock_presence_grpc.PresenceServiceStub.return_value = self.mock_presence_stub
                
                self.client = MidimoChatClient(
                    host="test-host",
                    port=12345
                )
    
    def test_initialization(self):
        """Test client initialization"""
        self.assertEqual(self.client.host, "test-host")
        self.assertEqual(self.client.port, 12345)
        self.assertEqual(self.client.service_name, "midimo_chat")
        self.assertEqual(self.client.channel, self.mock_channel)
    
    @mock.patch('core.microservices.midimo_chat.client.chat_pb2')
    def test_create_thread(self, mock_chat_pb2):
        """Test create_thread method"""
        # Mock request and response
        mock_request = mock.MagicMock()
        mock_chat_pb2.CreateThreadRequest.return_value = mock_request
        
        mock_response = mock.MagicMock()
        mock_thread = mock.MagicMock()
        mock_response.thread = mock_thread
        self.mock_chat_stub.CreateThread.return_value = mock_response
        
        # Call the method
        result = self.client.create_thread(
            user_id="user123",
            title="Test Thread",
            participants=["user456"],
            metadata={"key": "value"}
        )
        
        # Verify the request
        mock_chat_pb2.CreateThreadRequest.assert_called_once_with(
            user_id="user123",
            title="Test Thread",
            participants=["user456"],
            metadata={"key": "value"}
        )
        
        # Verify the stub call
        self.mock_chat_stub.CreateThread.assert_called_once_with(
            mock_request, 
            metadata=[], 
            timeout=10
        )
        
        # Verify the result
        self.assertEqual(result, mock_thread)
    
    @mock.patch('core.microservices.midimo_chat.client.chat_pb2')
    def test_send_message(self, mock_chat_pb2):
        """Test send_message method"""
        # Mock request and response
        mock_request = mock.MagicMock()
        mock_chat_pb2.SendMessageRequest.return_value = mock_request
        
        mock_response = mock.MagicMock()
        mock_message = mock.MagicMock()
        mock_response.message = mock_message
        self.mock_chat_stub.SendMessage.return_value = mock_response
        
        # Call the method
        result = self.client.send_message(
            thread_id="thread123",
            user_id="user123",
            content="Hello, world!",
            attachment_ids=["att1", "att2"]
        )
        
        # Verify the request
        mock_chat_pb2.SendMessageRequest.assert_called_once_with(
            thread_id="thread123",
            user_id="user123",
            content="Hello, world!",
            attachment_ids=["att1", "att2"]
        )
        
        # Verify the stub call
        self.mock_chat_stub.SendMessage.assert_called_once_with(
            mock_request, 
            metadata=[], 
            timeout=10
        )
        
        # Verify the result
        self.assertEqual(result, mock_message)
    
    @mock.patch('core.microservices.midimo_chat.client.presence_pb2')
    def test_update_presence(self, mock_presence_pb2):
        """Test update_presence method"""
        # Mock request and response
        mock_request = mock.MagicMock()
        mock_presence_pb2.UpdatePresenceRequest.return_value = mock_request
        
        mock_response = mock.MagicMock()
        mock_presence = mock.MagicMock()
        mock_response.presence = mock_presence
        self.mock_presence_stub.UpdatePresence.return_value = mock_response
        
        # Call the method
        result = self.client.update_presence(
            user_id="user123",
            status="ONLINE",
            custom_status="Working"
        )
        
        # Verify the request
        mock_presence_pb2.UpdatePresenceRequest.assert_called_once_with(
            user_id="user123",
            status="ONLINE",
            custom_status="Working"
        )
        
        # Verify the stub call
        self.mock_presence_stub.UpdatePresence.assert_called_once_with(
            mock_request, 
            metadata=[], 
            timeout=10
        )
        
        # Verify the result
        self.assertEqual(result, mock_presence)
    
    def test_retry_on_unavailable(self):
        """Test retry mechanism on UNAVAILABLE error"""
        # Mock grpc.RpcError with UNAVAILABLE status
        mock_error = mock.MagicMock(spec=grpc.RpcError)
        mock_error.code.return_value = grpc.StatusCode.UNAVAILABLE
        mock_error.details.return_value = "Service unavailable"
        
        # Mock request and method
        mock_request = mock.MagicMock()
        mock_method = mock.MagicMock(side_effect=[
            mock_error,  # First call fails
            mock_error,  # Second call fails
            mock.MagicMock()  # Third call succeeds
        ])
        
        # Mock reconnect
        with mock.patch.object(self.client, '_connect') as mock_connect:
            # Call with retry
            self.client._call_with_retry(
                method=mock_method,
                request=mock_request,
                max_retries=3
            )
            
            # Verify retries and reconnects
            self.assertEqual(mock_method.call_count, 3)
            self.assertEqual(mock_connect.call_count, 2)
    
    def test_exception_on_max_retries(self):
        """Test exception when max retries are exceeded"""
        # Mock grpc.RpcError with UNAVAILABLE status
        mock_error = mock.MagicMock(spec=grpc.RpcError)
        mock_error.code.return_value = grpc.StatusCode.UNAVAILABLE
        mock_error.details.return_value = "Service unavailable"
        
        # Mock request and method that always fails
        mock_request = mock.MagicMock()
        mock_method = mock.MagicMock(side_effect=mock_error)
        
        # Call with retry and expect exception
        with self.assertRaises(ServiceUnavailableError):
            self.client._call_with_retry(
                method=mock_method,
                request=mock_request,
                max_retries=3
            )
            
        # Verify retries
        self.assertEqual(mock_method.call_count, 3)
    
    def test_exception_on_deadline_exceeded(self):
        """Test exception on DEADLINE_EXCEEDED error"""
        # Mock grpc.RpcError with DEADLINE_EXCEEDED status
        mock_error = mock.MagicMock(spec=grpc.RpcError)
        mock_error.code.return_value = grpc.StatusCode.DEADLINE_EXCEEDED
        mock_error.details.return_value = "Deadline exceeded"
        
        # Mock request and method
        mock_request = mock.MagicMock()
        mock_method = mock.MagicMock(side_effect=mock_error)
        
        # Call and expect exception
        with self.assertRaises(ServiceTimeoutError):
            self.client._call_with_retry(
                method=mock_method,
                request=mock_request,
                max_retries=1
            )
    
    def test_close(self):
        """Test close method"""
        self.client.close()
        self.mock_channel.close.assert_called_once()
        self.assertIsNone(self.client.channel)
    
    def test_context_manager(self):
        """Test client as context manager"""
        with mock.patch('grpc.insecure_channel'):
            with mock.patch('core.microservices.midimo_chat.client.chat_pb2_grpc'):
                with mock.patch('core.microservices.midimo_chat.client.presence_pb2_grpc'):
                    with MidimoChatClient() as client:
                        self.assertIsNotNone(client.channel)
                    
                    # Channel should be closed after exiting context
                    self.assertIsNone(client.channel)
