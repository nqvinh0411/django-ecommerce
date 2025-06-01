from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from django.utils.timezone import now
from user_auth.models import UserToken

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            return None

        user, validated_token = result
        token_str = self.get_raw_token(self.get_header(request))

        try:
            user_token = UserToken.objects.get(user=user, token=token_str)
        except UserToken.DoesNotExist:
            raise AuthenticationFailed('Token không còn hợp lệ.')

        if user_token.expired_date < now():
            user_token.delete()
            raise AuthenticationFailed('Token đã hết hạn.')

        return (user, validated_token)
