"""
Utility functions for Midimo Chat integration
"""

import logging
import re
import subprocess
import os
from django.conf import settings

logger = logging.getLogger(__name__)


def generate_proto_files(proto_dir, output_dir=None):
    """
    Generate Python code from protobuf files
    
    Args:
        proto_dir: Directory containing .proto files
        output_dir: Output directory (defaults to same as proto_dir)
    
    Returns:
        True if successful, False otherwise
    """
    if output_dir is None:
        output_dir = proto_dir
    
    try:
        # Find all .proto files
        proto_files = [f for f in os.listdir(proto_dir) if f.endswith('.proto')]
        
        if not proto_files:
            logger.warning(f"No .proto files found in {proto_dir}")
            return False
        
        # Generate Python code for each file
        for proto_file in proto_files:
            proto_path = os.path.join(proto_dir, proto_file)
            
            # Run protoc command
            cmd = [
                'python', '-m', 'grpc_tools.protoc',
                f'--proto_path={proto_dir}',
                f'--python_out={output_dir}',
                f'--grpc_python_out={output_dir}',
                proto_path
            ]
            
            logger.info(f"Generating Python code from {proto_file}")
            subprocess.check_call(cmd)
        
        logger.info(f"Successfully generated protobuf code in {output_dir}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to generate protobuf code: {str(e)}")
        return False


def extract_thread_context(thread_metadata):
    """
    Extract E-commerce context from thread metadata
    
    Args:
        thread_metadata: Thread metadata dictionary
    
    Returns:
        Dict with extracted context (order_id, product_id, etc.)
    """
    context = {}
    
    if not thread_metadata:
        return context
    
    # Extract order_id if present
    if 'order_id' in thread_metadata:
        context['order_id'] = thread_metadata['order_id']
    
    # Extract product_id if present
    if 'product_id' in thread_metadata:
        context['product_id'] = thread_metadata['product_id']
    
    # Extract thread_type
    if 'thread_type' in thread_metadata:
        context['thread_type'] = thread_metadata['thread_type']
    
    return context


def get_user_display_name(user_id):
    """
    Get a user's display name for chat
    
    This should be integrated with your actual user system.
    
    Args:
        user_id: User ID
    
    Returns:
        Display name string
    """
    # This is a placeholder - in a real implementation,
    # this would look up the user in your database
    if user_id.startswith('support_agent_'):
        return f"Support Agent {user_id.split('_')[-1]}"
    elif user_id == 'system':
        return "System"
    else:
        return f"Customer {user_id}"


def format_thread_title(customer_id, order_id=None, product_id=None):
    """
    Format a thread title based on context
    
    Args:
        customer_id: Customer ID
        order_id: Optional order ID
        product_id: Optional product ID
    
    Returns:
        Formatted thread title
    """
    if order_id:
        return f"Support for Order #{order_id}"
    elif product_id:
        return f"Product Inquiry #{product_id}"
    else:
        return f"Customer Support {customer_id}"
