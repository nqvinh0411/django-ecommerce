import re
import uuid
from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


# Validators phổ biến cho tất cả API - định dạng regex chuẩn hóa

# Phone number validator - quốc tế theo chuẩn E.164
phone_regex = RegexValidator(
    regex=r'^\+?[1-9]\d{1,14}$',
    message=_('Số điện thoại phải theo chuẩn E.164, ví dụ: "+84901234567". Tối đa 15 chữ số.')
)

# Slug validator - cho URL và tài nguyên
slug_regex = RegexValidator(
    regex=r'^[a-z0-9]+(?:-[a-z0-9]+)*$',
    message=_('Slug chỉ có thể chứa chữ thường, số và dấu gạch ngang, không có khoảng trắng.')
)

# Email validator - theo chuẩn RFC 5322
email_regex = RegexValidator(
    regex=r'^[a-zA-Z0-9.!#$%&\'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$',
    message=_('Email không hợp lệ.')
)

# Username validator - cho tên đăng nhập
username_regex = RegexValidator(
    regex=r'^[a-zA-Z0-9._-]{3,30}$',
    message=_('Tên đăng nhập chỉ có thể chứa chữ cái, chữ số, dấu chấm, gạch dưới và gạch ngang. Độ dài từ 3-30 ký tự.')
)

# UUID validator - kiểm tra định dạng UUID hợp lệ 
uuid_regex = RegexValidator(
    regex=r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
    message=_('Định dạng UUID không hợp lệ.')
)


def validate_slug(value):
    """
    Kiểm tra tính hợp lệ của slug URL.
    
    Một slug hợp lệ cần đáp ứng các yêu cầu:
    - Chỉ chứa chữ thường, số và dấu gạch ngang
    - Không bắt đầu hoặc kết thúc bằng dấu gạch ngang
    - Không chứa hai dấu gạch ngang liên tiếp
    
    Args:
        value (str): Slug cần kiểm tra
        
    Returns:
        str: Slug nếu hợp lệ
        
    Raises:
        ValidationError: Nếu slug không đáp ứng yêu cầu
    """
    error_messages = {
        'format': _('Slug chỉ có thể chứa chữ thường, số và dấu gạch ngang.'),
        'bounds': _('Slug không thể bắt đầu hoặc kết thúc bằng dấu gạch ngang.'),
        'consecutive': _('Slug không thể chứa hai dấu gạch ngang liên tiếp.'),
    }
    
    if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', value):
        raise serializers.ValidationError(error_messages['format'])
    
    if value.startswith('-') or value.endswith('-'):
        raise serializers.ValidationError(error_messages['bounds'])
    
    if '--' in value:
        raise serializers.ValidationError(error_messages['consecutive'])
    
    return value


def validate_password(value):
    """
    Kiểm tra độ mạnh của mật khẩu theo chuẩn bảo mật chung.
    
    Mật khẩu hợp lệ cần đáp ứng các yêu cầu:
    - Tối thiểu 8 ký tự
    - Chứa ít nhất một chữ số
    - Chứa ít nhất một chữ cái
    - Chứa ít nhất một chữ viết hoa
    - Chứa ít nhất một ký tự đặc biệt (tùy chọn, có thể bật/tắt)
    
    Args:
        value (str): Mật khẩu cần kiểm tra
        
    Returns:
        str: Mật khẩu nếu hợp lệ
        
    Raises:
        ValidationError: Nếu mật khẩu không đáp ứng yêu cầu
    """
    error_messages = {
        'min_length': _('Mật khẩu phải có ít nhất 8 ký tự.'),
        'digit': _('Mật khẩu phải chứa ít nhất một chữ số.'),
        'letter': _('Mật khẩu phải chứa ít nhất một chữ cái.'),
        'upper': _('Mật khẩu phải chứa ít nhất một chữ viết hoa.'),
        'special': _('Mật khẩu phải chứa ít nhất một ký tự đặc biệt (@, #, $, %, v.v.).'),
    }
    
    # Yêu cầu về độ dài tối thiểu
    if len(value) < 8:
        raise serializers.ValidationError(error_messages['min_length'])
    
    # Yêu cầu về chữ số
    if not any(char.isdigit() for char in value):
        raise serializers.ValidationError(error_messages['digit'])
    
    # Yêu cầu về chữ cái
    if not any(char.isalpha() for char in value):
        raise serializers.ValidationError(error_messages['letter'])
    
    # Yêu cầu về chữ viết hoa
    if not any(char.isupper() for char in value):
        raise serializers.ValidationError(error_messages['upper'])
    
    # Tùy chọn: Yêu cầu về ký tự đặc biệt
    # Có thể bật/tắt dựa trên cấu hình
    # if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
    #     raise serializers.ValidationError(error_messages['special'])
    
    return value


def validate_uuid(value):
    """
    Kiểm tra tính hợp lệ của UUID.
    
    Args:
        value (str): UUID cần kiểm tra, dạng chuỗi
        
    Returns:
        str: UUID hợp lệ, đã được chuẩn hóa
        
    Raises:
        ValidationError: Nếu UUID không hợp lệ
    """
    try:
        # Kiểm tra xem có phải UUID hợp lệ
        uuid_obj = uuid.UUID(str(value))
        # Trả về UUID đã được chuẩn hóa (lowercase, có dấu gạch ngang)
        return str(uuid_obj)
    except (ValueError, AttributeError, TypeError):
        raise serializers.ValidationError(_('Định dạng UUID không hợp lệ.'))


def validate_iso_date(value):
    """
    Kiểm tra định dạng ngày tháng theo chuẩn ISO 8601 (YYYY-MM-DD).
    
    Args:
        value (str): Chuỗi ngày tháng cần kiểm tra
        
    Returns:
        str: Chuỗi ngày tháng nếu hợp lệ
        
    Raises:
        ValidationError: Nếu định dạng không đúng chuẩn ISO 8601
    """
    iso_date_pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(iso_date_pattern, value):
        raise serializers.ValidationError(_('Ngày tháng phải theo định dạng ISO 8601 (YYYY-MM-DD).'))
    return value


def validate_iso_datetime(value):
    """
    Kiểm tra định dạng ngày giờ theo chuẩn ISO 8601 (YYYY-MM-DDThh:mm:ss[.mmm]Z).
    
    Args:
        value (str): Chuỗi ngày giờ cần kiểm tra
        
    Returns:
        str: Chuỗi ngày giờ nếu hợp lệ
        
    Raises:
        ValidationError: Nếu định dạng không đúng chuẩn ISO 8601
    """
    iso_datetime_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$'
    if not re.match(iso_datetime_pattern, value):
        raise serializers.ValidationError(_('Thời gian phải theo định dạng ISO 8601 (YYYY-MM-DDThh:mm:ssZ).'))
    return value


# Validator cho trường JSON
def validate_json_structure(value, required_fields=None, optional_fields=None):
    """
    Kiểm tra cấu trúc của JSON theo các trường bắt buộc và tùy chọn.
    
    Args:
        value (dict): Dữ liệu JSON cần kiểm tra
        required_fields (list, optional): Danh sách các trường bắt buộc
        optional_fields (list, optional): Danh sách các trường tùy chọn
        
    Returns:
        dict: Dữ liệu JSON nếu hợp lệ
        
    Raises:
        ValidationError: Nếu JSON thiếu trường bắt buộc hoặc có trường không được phép
    """
    if not isinstance(value, dict):
        raise serializers.ValidationError(_('Dữ liệu phải là một đối tượng JSON hợp lệ.'))
    
    errors = {}
    
    # Kiểm tra các trường bắt buộc
    if required_fields:
        missing_fields = [field for field in required_fields if field not in value]
        if missing_fields:
            errors['missing_fields'] = _('Các trường bắt buộc sau đây bị thiếu: {}.').format(', '.join(missing_fields))
    
    # Kiểm tra các trường không được phép
    if required_fields or optional_fields:
        allowed_fields = set((required_fields or []) + (optional_fields or []))
        unknown_fields = [field for field in value if field not in allowed_fields]
        if unknown_fields:
            errors['unknown_fields'] = _('Các trường sau đây không được phép: {}.').format(', '.join(unknown_fields))
    
    if errors:
        raise serializers.ValidationError(errors)
    
    return value
