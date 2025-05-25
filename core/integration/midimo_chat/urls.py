"""
Midimo Chat Integration URL Configuration.

Module này định nghĩa các URL routes liên quan đến tích hợp Midimo Chat.
"""

from django.urls import path
from .webhooks import webhook_handler

urlpatterns = [
    path('webhooks/', webhook_handler, name='midimo_chat_webhook'),
]
