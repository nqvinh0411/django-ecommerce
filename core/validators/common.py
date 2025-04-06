import re
from django.core.validators import RegexValidator
from rest_framework import serializers


# Phone number validator
phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Số điện thoại phải ở định dạng: '+999999999'. Cho phép từ 9 đến 15 chữ số."
)

# Slug validator
slug_regex = RegexValidator(
    regex=r'^[a-z0-9]+(?:-[a-z0-9]+)*$',
    message="Slug chỉ có thể chứa chữ thường, số và dấu gạch ngang."
)

# Email validator
email_regex = RegexValidator(
    regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    message="Email không hợp lệ."
)


def validate_slug(value):
    """
    Custom validator for slug fields that checks additional rules.
    """
    if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', value):
        raise serializers.ValidationError(
            "Slug chỉ có thể chứa chữ thường, số và dấu gạch ngang."
        )
    if value.startswith('-') or value.endswith('-'):
        raise serializers.ValidationError(
            "Slug không thể bắt đầu hoặc kết thúc bằng dấu gạch ngang."
        )
    if '--' in value:
        raise serializers.ValidationError(
            "Slug không thể chứa hai dấu gạch ngang liên tiếp."
        )
    return value


def validate_password(value):
    """
    Validate that the password is strong enough.
    """
    if len(value) < 8:
        raise serializers.ValidationError(
            "Mật khẩu phải có ít nhất 8 ký tự."
        )
    if not any(char.isdigit() for char in value):
        raise serializers.ValidationError(
            "Mật khẩu phải chứa ít nhất một chữ số."
        )
    if not any(char.isalpha() for char in value):
        raise serializers.ValidationError(
            "Mật khẩu phải chứa ít nhất một chữ cái."
        )
    if not any(char.isupper() for char in value):
        raise serializers.ValidationError(
            "Mật khẩu phải chứa ít nhất một chữ viết hoa."
        )
    return value
