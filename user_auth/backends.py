from __future__ import annotations

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class EmailBackend(ModelBackend):
    """
    Custom authentication backend allows users to log in using their email address.

    This backend keeps all security checks from Django's ModelBackend (including
    `is_active` flag) but looks up the user by `email` instead of `username`.
    """

    def authenticate(self, request, email: str | None = None, password: str | None = None, **kwargs):
        """Authenticate user by email instead of username"""
        if email is None or password is None:
            return None

        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=email)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except UserModel.DoesNotExist:
            return None
        
        return None 