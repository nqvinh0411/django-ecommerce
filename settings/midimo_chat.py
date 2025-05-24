"""
Settings for Midimo Chat integration
"""

# Midimo Chat connection settings
MIDIMO_CHAT_HOST = "localhost"  # Change to actual host in production
MIDIMO_CHAT_PORT = 50051        # Default gRPC port
MIDIMO_CHAT_SECURE = False      # Set to True in production

# JWT authentication for Midimo Chat
MIDIMO_CHAT_JWT_SECRET_KEY = "your-secret-key-here"  # Change in production
MIDIMO_CHAT_JWT_ISSUER = "e_commerce"
MIDIMO_CHAT_JWT_AUDIENCE = "midimo_chat"

# User IDs
SYSTEM_USER_ID = "system"
DEFAULT_SUPPORT_AGENT_ID = "support_agent_1"
SUPPORT_AGENT_IDS = ["support_agent_1", "support_agent_2", "support_agent_3"]

# Logging configuration for Midimo Chat
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/midimo_chat.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'core.microservices': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
