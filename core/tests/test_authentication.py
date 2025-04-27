from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken

from core.authentication.tokens import get_tokens_for_user, configure_token_settings

User = get_user_model()


class TestTokens(TestCase):
    """Test cases for token utility functions."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
    
    def test_get_tokens_for_user(self):
        """Test that tokens are correctly generated for a user."""
        tokens = get_tokens_for_user(self.user)
        
        # Verify the structure of the returned tokens
        self.assertIn('refresh', tokens)
        self.assertIn('access', tokens)
        
        # Verify the tokens are strings (not objects)
        self.assertIsInstance(tokens['refresh'], str)
        self.assertIsInstance(tokens['access'], str)
        
        # Verify the tokens are valid by decoding them
        refresh_token = RefreshToken(tokens['refresh'])
        self.assertEqual(refresh_token['user_id'], self.user.id)
    
    def test_configure_token_settings(self):
        """Test that token settings are correctly configured."""
        token_settings = configure_token_settings()
        
        # Verify essential settings
        self.assertIn('ACCESS_TOKEN_LIFETIME', token_settings)
        self.assertIn('REFRESH_TOKEN_LIFETIME', token_settings)
        self.assertIn('ROTATE_REFRESH_TOKENS', token_settings)
        self.assertIn('BLACKLIST_AFTER_ROTATION', token_settings)
        self.assertIn('SIGNING_KEY', token_settings)
        
        # Verify types
        self.assertIsInstance(token_settings['ACCESS_TOKEN_LIFETIME'], timedelta)
        self.assertIsInstance(token_settings['REFRESH_TOKEN_LIFETIME'], timedelta)
        self.assertEqual(token_settings['SIGNING_KEY'], settings.SECRET_KEY)
        
        # Verify specific values
        self.assertEqual(token_settings['ACCESS_TOKEN_LIFETIME'], timedelta(minutes=60))
        self.assertEqual(token_settings['REFRESH_TOKEN_LIFETIME'], timedelta(days=7))
        self.assertTrue(token_settings['ROTATE_REFRESH_TOKENS'])
        self.assertTrue(token_settings['BLACKLIST_AFTER_ROTATION'])
