"""
Tests for Midimo Chat services
"""

import unittest
from unittest import mock
from django.test import TestCase
from django.conf import settings

from ..midimo_chat.services import ChatService, PresenceService


class ChatServiceTests(TestCase):
    """Test cases for ChatService"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock the MidimoChatClient
        self.mock_client = mock.MagicMock()
        self.service = ChatService(client=self.mock_client)
    
    def test_create_support_thread(self):
        """Test create_support_thread method"""
        # Mock thread response
        mock_thread = mock.MagicMock()
        mock_thread.id = "thread123"
        self.mock_client.create_thread.return_value = mock_thread
        
        # Call the method
        result = self.service.create_support_thread(
            customer_id="customer123",
            order_id="order456",
            product_id="product789"
        )
        
        # Verify client call
        self.mock_client.create_thread.assert_called_once()
        args, kwargs = self.mock_client.create_thread.call_args
        
        # Check args
        self.assertEqual(kwargs["user_id"], "customer123")
        self.assertIn("Customer Support", kwargs["title"])
        self.assertIsInstance(kwargs["participants"], list)
        self.assertIsInstance(kwargs["metadata"], dict)
        
        # Check metadata
        metadata = kwargs["metadata"]
        self.assertEqual(metadata["source"], "e_commerce")
        self.assertEqual(metadata["thread_type"], "customer_support")
        self.assertEqual(metadata["order_id"], "order456")
        self.assertEqual(metadata["product_id"], "product789")
        
        # Check result
        self.assertEqual(result, mock_thread)
    
    def test_send_order_update_message(self):
        """Test send_order_update_message method"""
        # Mock message response
        mock_message = mock.MagicMock()
        self.mock_client.send_message.return_value = mock_message
        
        # Set system user ID
        with self.settings(SYSTEM_USER_ID="system_bot"):
            # Call the method
            result = self.service.send_order_update_message(
                thread_id="thread123",
                order_id="order456",
                status="Shipped",
                message="Your order has been shipped!"
            )
            
            # Verify client call
            self.mock_client.send_message.assert_called_once()
            args, kwargs = self.mock_client.send_message.call_args
            
            # Check args
            self.assertEqual(kwargs["thread_id"], "thread123")
            self.assertEqual(kwargs["user_id"], "system_bot")
            self.assertIn("order456", kwargs["content"])
            self.assertIn("Shipped", kwargs["content"])
            self.assertIn("Your order has been shipped!", kwargs["content"])
            
            # Check result
            self.assertEqual(result, mock_message)


class PresenceServiceTests(TestCase):
    """Test cases for PresenceService"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock the MidimoChatClient
        self.mock_client = mock.MagicMock()
        self.service = PresenceService(client=self.mock_client)
    
    def test_set_user_online(self):
        """Test set_user_online method"""
        # Call the method
        self.service.set_user_online(
            user_id="user123",
            custom_status="Available for chat"
        )
        
        # Verify client call
        self.mock_client.update_presence.assert_called_once_with(
            user_id="user123",
            status="ONLINE",
            custom_status="Available for chat"
        )
    
    def test_set_user_offline(self):
        """Test set_user_offline method"""
        # Call the method
        self.service.set_user_offline(user_id="user123")
        
        # Verify client call
        self.mock_client.update_presence.assert_called_once_with(
            user_id="user123",
            status="OFFLINE"
        )
    
    def test_get_agent_availability(self):
        """Test get_agent_availability method"""
        # Mock presence data
        mock_presence1 = mock.MagicMock()
        mock_presence1.user_id = "agent1"
        mock_presence1.status = "ONLINE"
        
        mock_presence2 = mock.MagicMock()
        mock_presence2.user_id = "agent2"
        mock_presence2.status = "AWAY"
        
        self.mock_client.get_presence.return_value = {
            "agent1": mock_presence1,
            "agent2": mock_presence2
        }
        
        # Call the method
        result = self.service.get_agent_availability(
            agent_ids=["agent1", "agent2", "agent3"]
        )
        
        # Verify client call
        self.mock_client.get_presence.assert_called_once_with(
            ["agent1", "agent2", "agent3"]
        )
        
        # Check result
        self.assertEqual(result, {
            "agent1": True,
            "agent2": False,
            "agent3": False
        })
    
    def test_start_typing(self):
        """Test start_typing method"""
        # Call the method
        self.service.start_typing(
            thread_id="thread123",
            user_id="user123"
        )
        
        # Verify client call
        self.mock_client.update_typing_status.assert_called_once_with(
            thread_id="thread123",
            user_id="user123",
            is_typing=True
        )
    
    def test_stop_typing(self):
        """Test stop_typing method"""
        # Call the method
        self.service.stop_typing(
            thread_id="thread123",
            user_id="user123"
        )
        
        # Verify client call
        self.mock_client.update_typing_status.assert_called_once_with(
            thread_id="thread123",
            user_id="user123",
            is_typing=False
        )
