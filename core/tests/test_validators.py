from django.test import TestCase
from rest_framework import serializers

from core.validators.common import (
    phone_regex, slug_regex, email_regex,
    validate_slug, validate_password
)


class TestRegexValidators(TestCase):
    """Test cases for regex validators."""
    
    def test_phone_regex_valid(self):
        """Test phone_regex with valid phone numbers."""
        valid_phones = [
            '+84912345678',
            '0912345678',
            '+12345678901',
            '123456789012'
        ]
        
        for phone in valid_phones:
            try:
                phone_regex(phone)
            except Exception as e:
                self.fail(f"phone_regex raised exception for valid phone: {phone}, error: {e}")
    
    def test_phone_regex_invalid(self):
        """Test phone_regex with invalid phone numbers."""
        invalid_phones = [
            'abc123',
            '+84@12345678',
            '123',
            '+84 912 345 678',  # Spaces not allowed
        ]
        
        for phone in invalid_phones:
            with self.assertRaises(serializers.ValidationError):
                phone_regex(phone)
    
    def test_slug_regex_valid(self):
        """Test slug_regex with valid slugs."""
        valid_slugs = [
            'test-slug',
            'product123',
            'category-name-2',
            'a-b-c',
        ]
        
        for slug in valid_slugs:
            try:
                slug_regex(slug)
            except Exception as e:
                self.fail(f"slug_regex raised exception for valid slug: {slug}, error: {e}")
    
    def test_slug_regex_invalid(self):
        """Test slug_regex with invalid slugs."""
        invalid_slugs = [
            'Test-Slug',  # Contains uppercase
            'product_123',  # Contains underscore
            'category name',  # Contains space
            '@special-chars',  # Contains special chars
        ]
        
        for slug in invalid_slugs:
            with self.assertRaises(serializers.ValidationError):
                slug_regex(slug)
    
    def test_email_regex_valid(self):
        """Test email_regex with valid emails."""
        valid_emails = [
            'user@example.com',
            'firstname.lastname@domain.co.uk',
            'user.name+tag@example.org',
            'x@example.com',
            'user-name@domain.com',
        ]
        
        for email in valid_emails:
            try:
                email_regex(email)
            except Exception as e:
                self.fail(f"email_regex raised exception for valid email: {email}, error: {e}")
    
    def test_email_regex_invalid(self):
        """Test email_regex with invalid emails."""
        invalid_emails = [
            'user@.com',
            '@example.com',
            'user@example',
            'user@example..com',
            'user name@example.com',  # Space not allowed
        ]
        
        for email in invalid_emails:
            with self.assertRaises(serializers.ValidationError):
                email_regex(email)


class TestSlugValidator(TestCase):
    """Test cases for validate_slug function."""
    
    def test_validate_slug_valid(self):
        """Test validate_slug with valid slugs."""
        valid_slugs = [
            'test-slug',
            'product123',
            'category-name-2',
            'a-b-c',
        ]
        
        for slug in valid_slugs:
            try:
                result = validate_slug(slug)
                self.assertEqual(result, slug)  # Validator should return the value if valid
            except Exception as e:
                self.fail(f"validate_slug raised exception for valid slug: {slug}, error: {e}")
    
    def test_validate_slug_invalid_format(self):
        """Test validate_slug with invalid format slugs."""
        invalid_format_slugs = [
            'Test-Slug',  # Contains uppercase
            'product_123',  # Contains underscore
            'category name',  # Contains space
            '@special-chars',  # Contains special chars
        ]
        
        for slug in invalid_format_slugs:
            with self.assertRaises(serializers.ValidationError):
                validate_slug(slug)
    
    def test_validate_slug_invalid_start_end(self):
        """Test validate_slug with slugs starting or ending with hyphens."""
        invalid_start_end_slugs = [
            '-test-slug',  # Starts with hyphen
            'product123-',  # Ends with hyphen
            '-category-',  # Both starts and ends with hyphen
        ]
        
        for slug in invalid_start_end_slugs:
            with self.assertRaises(serializers.ValidationError):
                validate_slug(slug)
    
    def test_validate_slug_consecutive_hyphens(self):
        """Test validate_slug with slugs containing consecutive hyphens."""
        invalid_consecutive_hyphen_slugs = [
            'test--slug',
            'product---123',
            'a--b--c',
        ]
        
        for slug in invalid_consecutive_hyphen_slugs:
            with self.assertRaises(serializers.ValidationError):
                validate_slug(slug)


class TestPasswordValidator(TestCase):
    """Test cases for validate_password function."""
    
    def test_validate_password_valid(self):
        """Test validate_password with valid passwords."""
        valid_passwords = [
            'Password123',
            'StrongP@ssw0rd',
            'Abcdef12345',
            'P@ssw0rd!',
        ]
        
        for password in valid_passwords:
            try:
                result = validate_password(password)
                self.assertEqual(result, password)
            except Exception as e:
                self.fail(f"validate_password raised exception for valid password: {password}, error: {e}")
    
    def test_validate_password_too_short(self):
        """Test validate_password with passwords that are too short."""
        short_passwords = [
            'Abc123',  # 6 chars
            'Pass1',   # 5 chars
            'Ab1',     # 3 chars
        ]
        
        for password in short_passwords:
            with self.assertRaises(serializers.ValidationError) as context:
                validate_password(password)
            self.assertIn("Mật khẩu phải có ít nhất 8 ký tự", str(context.exception))
    
    def test_validate_password_no_digit(self):
        """Test validate_password with passwords without digits."""
        no_digit_passwords = [
            'PasswordOnly',
            'StrongPassword',
            'AbcdefGhijkl',
        ]
        
        for password in no_digit_passwords:
            with self.assertRaises(serializers.ValidationError) as context:
                validate_password(password)
            self.assertIn("Mật khẩu phải chứa ít nhất một chữ số", str(context.exception))
    
    def test_validate_password_no_letter(self):
        """Test validate_password with passwords without letters."""
        no_letter_passwords = [
            '12345678',
            '123456789',
            '1234567890',
        ]
        
        for password in no_letter_passwords:
            with self.assertRaises(serializers.ValidationError) as context:
                validate_password(password)
            self.assertIn("Mật khẩu phải chứa ít nhất một chữ cái", str(context.exception))
    
    def test_validate_password_no_uppercase(self):
        """Test validate_password with passwords without uppercase letters."""
        no_uppercase_passwords = [
            'password123',
            'strongp@ssw0rd',
            'abcdef12345',
        ]
        
        for password in no_uppercase_passwords:
            with self.assertRaises(serializers.ValidationError) as context:
                validate_password(password)
            self.assertIn("Mật khẩu phải chứa ít nhất một chữ viết hoa", str(context.exception))
