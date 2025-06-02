from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import RegexValidator
import uuid

User = get_user_model()


class UserToken(models.Model):
    """
    Legacy token model for backward compatibility.
    Will be migrated to UserSession gradually.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_auth_tokens')
    token = models.CharField(max_length=255, unique=True)
    created_date = models.DateTimeField(auto_now_add=True)
    expired_date = models.DateTimeField()
    device_name = models.CharField(max_length=100, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{} - {}".format(self.user.username, self.token[:10])
    
    def is_expired(self):
        return self.expired_date < timezone.now()

    class Meta:
        db_table = 'user_auth_usertoken'


class UserSession(models.Model):
    """
    Enhanced session tracking for JWT tokens and device information.
    This will replace UserToken in the future.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='auth_sessions',
        verbose_name='User'
    )
    session_key = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Session Key',
        help_text='JWT token identifier or session key'
    )
    
    # Device information
    device_name = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name='Device Name'
    )
    device_type = models.CharField(
        max_length=50,
        choices=[
            ('web', 'Web Browser'),
            ('mobile', 'Mobile App'),
            ('desktop', 'Desktop App'),
            ('tablet', 'Tablet'),
            ('unknown', 'Unknown'),
        ],
        default='unknown',
        verbose_name='Device Type'
    )
    
    # Network information
    ip_address = models.GenericIPAddressField(
        blank=True, 
        null=True,
        verbose_name='IP Address'
    )
    user_agent = models.TextField(
        blank=True, 
        null=True,
        verbose_name='User Agent'
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Location',
        help_text='City, Country from IP'
    )
    
    # Session lifecycle
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )
    expires_at = models.DateTimeField(
        verbose_name='Expires At'
    )
    last_activity = models.DateTimeField(
        auto_now=True,
        verbose_name='Last Activity'
    )
    
    # Session status
    is_active = models.BooleanField(
        default=True,
        verbose_name='Is Active'
    )
    logout_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Logged Out At'
    )
    
    class Meta:
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key']),
            models.Index(fields=['expires_at']),
        ]
        db_table = 'user_auth_usersession'
    
    def __str__(self):
        return f"{self.user.email} - {self.device_name or 'Unknown Device'}"
    
    def is_expired(self):
        """Check if session is expired"""
        return self.expires_at < timezone.now()
    
    def extend_session(self, hours=24):
        """Extend session expiry"""
        self.expires_at = timezone.now() + timezone.timedelta(hours=hours)
        self.save(update_fields=['expires_at'])
    
    def logout(self):
        """Mark session as logged out"""
        self.is_active = False
        self.logout_at = timezone.now()
        self.save(update_fields=['is_active', 'logout_at'])


class LoginHistory(models.Model):
    """
    Enhanced login history tracking.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='user_auth_login_histories',
        verbose_name='User'
    )
    session = models.ForeignKey(
        UserSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='login_records',
        verbose_name='Session'
    )
    
    # Legacy field for backward compatibility
    token_ref = models.CharField(max_length=255, blank=True, null=True)
    
    # Login details
    login_method = models.CharField(
        max_length=50,
        choices=[
            ('password', 'Password'),
            ('social', 'Social Login'),
            ('token', 'Token'),
            ('api', 'API Key'),
        ],
        default='password',
        verbose_name='Login Method'
    )
    
    # Device and network info
    device_name = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name='Device Name'
    )
    ip_address = models.GenericIPAddressField(
        blank=True, 
        null=True,
        verbose_name='IP Address'
    )
    user_agent = models.TextField(
        blank=True, 
        null=True,
        verbose_name='User Agent'
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Location'
    )
    
    # Timestamps - keep legacy field names for compatibility
    login_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Login Time'
    )
    logout_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Logout Time'
    )
    
    # Status tracking
    login_successful = models.BooleanField(
        default=True,
        verbose_name='Login Successful'
    )
    failure_reason = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Failure Reason'
    )

    def __str__(self):
        return "{} - {}".format(self.user.username, self.login_date)
    
    @property
    def session_duration(self):
        """Calculate session duration if logged out"""
        if self.logout_date:
            return self.logout_date - self.login_date
        return None
    
    class Meta:
        db_table = 'user_auth_loginhistory'
        verbose_name = 'Login History'
        verbose_name_plural = 'Login Histories'
        ordering = ['-login_date']
        indexes = [
            models.Index(fields=['user', 'login_date']),
            models.Index(fields=['login_successful']),
            models.Index(fields=['ip_address']),
        ]


class PasswordResetToken(models.Model):
    """
    Password reset token management.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='auth_password_reset_tokens',
        verbose_name='User'
    )
    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        verbose_name='Reset Token'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )
    expires_at = models.DateTimeField(
        verbose_name='Expires At'
    )
    used_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Used At'
    )
    is_used = models.BooleanField(
        default=False,
        verbose_name='Is Used'
    )
    
    class Meta:
        verbose_name = 'Password Reset Token'
        verbose_name_plural = 'Password Reset Tokens'
        ordering = ['-created_at']
        db_table = 'user_auth_passwordresettoken'
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user', 'is_used']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - Reset Token"
    
    def is_expired(self):
        """Check if token is expired"""
        return self.expires_at < timezone.now()
    
    def is_valid(self):
        """Check if token is valid (not used and not expired)"""
        return not self.is_used and not self.is_expired()
    
    def mark_as_used(self):
        """Mark token as used"""
        self.is_used = True
        self.used_at = timezone.now()
        self.save(update_fields=['is_used', 'used_at'])
    
    def save(self, *args, **kwargs):
        # Set expiry to 1 hour from creation if not set
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(hours=1)
        super().save(*args, **kwargs) 