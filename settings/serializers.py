from rest_framework import serializers
from .models import StoreSetting, Currency, LanguageSetting, EmailTemplate


class StoreSettingSerializer(serializers.ModelSerializer):
    """
    Serializer for StoreSetting model.
    """
    class Meta:
        model = StoreSetting
        fields = [
            'id', 'store_name', 'store_logo', 'support_email', 'phone_number',
            'address', 'default_currency', 'default_language', 'is_maintenance_mode',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CurrencySerializer(serializers.ModelSerializer):
    """
    Serializer for Currency model.
    """
    class Meta:
        model = Currency
        fields = [
            'id', 'code', 'name', 'symbol', 'exchange_rate_to_base',
            'is_default', 'is_active'
        ]
        read_only_fields = ['id']


class LanguageSettingSerializer(serializers.ModelSerializer):
    """
    Serializer for LanguageSetting model.
    """
    class Meta:
        model = LanguageSetting
        fields = [
            'id', 'code', 'name', 'is_default', 'is_active'
        ]
        read_only_fields = ['id']


class EmailTemplateSerializer(serializers.ModelSerializer):
    """
    Serializer for EmailTemplate model.
    Validates that template_key is unique and content is not empty.
    """
    class Meta:
        model = EmailTemplate
        fields = [
            'id', 'template_key', 'subject', 'body_html', 'body_text',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_template_key(self, value):
        """
        Ensure template_key is unique when creating a new template.
        """
        instance = self.instance
        if EmailTemplate.objects.filter(template_key=value).exists() and (instance is None or instance.template_key != value):
            raise serializers.ValidationError("A template with this key already exists.")
        return value

    def validate(self, attrs):
        """
        Validate that both body_html and body_text are not empty.
        """
        body_html = attrs.get('body_html', '')
        body_text = attrs.get('body_text', '')

        if not body_html.strip():
            raise serializers.ValidationError({"body_html": "HTML body cannot be empty."})

        if not body_text.strip():
            raise serializers.ValidationError({"body_text": "Text body cannot be empty."})

        return attrs
