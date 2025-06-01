from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class UserToken(models.Model):
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


class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_auth_login_histories')
    token_ref = models.CharField(max_length=255, blank=True, null=True)
    device_name = models.CharField(max_length=100, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    login_date = models.DateTimeField(auto_now_add=True)
    logout_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return "{} - {}".format(self.user.username, self.login_date)
    
    class Meta:
        db_table = 'user_auth_loginhistory' 