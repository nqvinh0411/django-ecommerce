"""
High-level service wrappers for Midimo Chat
"""

import logging
from django.conf import settings
from .client import MidimoChatClient

logger = logging.getLogger(__name__)


class ChatService:
    """
    High-level service for chat operations
    
    Provides simplified interfaces to the Midimo Chat gRPC client
    for common chat operations used by E-commerce.
    """
    
    def __init__(self, client=None):
        """
        Initialize with a MidimoChatClient
        
        Args:
            client: MidimoChatClient instance (creates one if None)
        """
        self.client = client or MidimoChatClient()
    
    def create_support_thread(self, customer_id, order_id=None, product_id=None):
        """
        Create a new customer support thread
        
        Args:
            customer_id: ID of the customer
            order_id: Optional related order ID
            product_id: Optional related product ID
        
        Returns:
            Thread object
        """
        # Determine the support agent assignment
        # In a real implementation, this would use a routing algorithm
        support_agent_id = self._get_available_support_agent()
        
        # Create metadata with e-commerce context
        metadata = {
            'source': 'e_commerce',
            'thread_type': 'customer_support',
        }
        
        if order_id:
            metadata['order_id'] = str(order_id)
        
        if product_id:
            metadata['product_id'] = str(product_id)
        
        # Create the thread
        thread = self.client.create_thread(
            user_id=customer_id,
            title=f"Customer Support {order_id or ''}",
            participants=[support_agent_id],
            metadata=metadata
        )
        
        logger.info(
            f"Created support thread {thread.id} for customer {customer_id} "
            f"with agent {support_agent_id}"
        )
        
        return thread
    
    def send_order_update_message(self, thread_id, order_id, status, message=None):
        """
        Send an order update message to a thread
        
        Args:
            thread_id: ID of the thread
            order_id: ID of the order
            status: New order status
            message: Optional additional message
        
        Returns:
            Message object
        """
        # Format content with order details
        content = f"Order #{order_id} status updated to: {status}"
        if message:
            content += f"\n\n{message}"
        
        # Use the system user ID for automated messages
        system_user_id = getattr(settings, "SYSTEM_USER_ID", "system")
        
        # Send the message
        message = self.client.send_message(
            thread_id=thread_id,
            user_id=system_user_id,
            content=content
        )
        
        logger.info(f"Sent order update message to thread {thread_id} for order {order_id}")
        
        return message
    
    def _get_available_support_agent(self):
        """
        Get an available support agent
        
        In a real implementation, this would check agent availability
        and workload to determine the best agent to assign.
        
        Returns:
            User ID of the selected support agent
        """
        # For simplicity, return a default agent ID
        # In production, implement a proper routing algorithm
        return getattr(settings, "DEFAULT_SUPPORT_AGENT_ID", "support_agent_1")


class PresenceService:
    """
    High-level service for presence operations
    
    Provides simplified interfaces to the Midimo Chat gRPC client
    for presence and typing status operations.
    """
    
    def __init__(self, client=None):
        """
        Initialize with a MidimoChatClient
        
        Args:
            client: MidimoChatClient instance (creates one if None)
        """
        self.client = client or MidimoChatClient()
    
    def set_user_online(self, user_id, custom_status=None):
        """
        Set a user's status to online
        
        Args:
            user_id: ID of the user
            custom_status: Optional custom status message
        """
        self.client.update_presence(
            user_id=user_id,
            status="ONLINE",
            custom_status=custom_status
        )
        
        logger.debug(f"Set user {user_id} status to ONLINE")
    
    def set_user_offline(self, user_id):
        """
        Set a user's status to offline
        
        Args:
            user_id: ID of the user
        """
        self.client.update_presence(
            user_id=user_id,
            status="OFFLINE"
        )
        
        logger.debug(f"Set user {user_id} status to OFFLINE")
    
    def get_agent_availability(self, agent_ids=None):
        """
        Get availability of support agents
        
        Args:
            agent_ids: List of agent IDs (uses defaults if None)
        
        Returns:
            Dict mapping agent_id to availability (True/False)
        """
        # Use provided agent IDs or get from settings
        if agent_ids is None:
            agent_ids = getattr(settings, "SUPPORT_AGENT_IDS", ["support_agent_1"])
        
        # Get presence data for agents
        presence_data = self.client.get_presence(agent_ids)
        
        # Convert to a simple availability dict
        availability = {}
        for agent_id in agent_ids:
            # Agent is available if online and not away
            if agent_id in presence_data:
                status = presence_data[agent_id].status
                availability[agent_id] = (status == "ONLINE")
            else:
                availability[agent_id] = False
        
        return availability
    
    def start_typing(self, thread_id, user_id):
        """
        Indicate that a user started typing in a thread
        
        Args:
            thread_id: ID of the thread
            user_id: ID of the user
        """
        self.client.update_typing_status(
            thread_id=thread_id,
            user_id=user_id,
            is_typing=True
        )
    
    def stop_typing(self, thread_id, user_id):
        """
        Indicate that a user stopped typing in a thread
        
        Args:
            thread_id: ID of the thread
            user_id: ID of the user
        """
        self.client.update_typing_status(
            thread_id=thread_id,
            user_id=user_id,
            is_typing=False
        )
