from __future__ import annotations

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class EmailBackend(ModelBackend):
    """Custom authentication backend allows users to log in using their email address.

    This backend keeps all security checks from Django's ModelBackend (including
    `is_active` flag) but looks up the user by `email` instead of `username`.
    """

    def authenticate(self, request, username: str | None = None, password: str | None = None, **kwargs):  # type: ignore[override]
        # `username` here actually contains the email sent from the frontend.
        if username is None or password is None:
            return None

        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
