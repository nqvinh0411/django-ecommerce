from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from .models import StoreSetting, Currency, LanguageSetting, EmailTemplate
from .serializers import (
    StoreSettingSerializer, CurrencySerializer,
    LanguageSettingSerializer, EmailTemplateSerializer
)


class StoreSettingView(generics.RetrieveUpdateAPIView):
    """
    API view to retrieve or update store settings.
    Only one instance exists and only admin users can access it.
    """
    serializer_class = StoreSettingSerializer
    permission_classes = [IsAdminUser]
    
    def get_object(self):
        """
        Get or create the store settings instance.
        """
        return StoreSetting.get_settings()


class CurrencyListView(generics.ListAPIView):
    """
    API view to list all currencies.
    Admin only access.
    """
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [IsAdminUser]


class LanguageSettingListView(generics.ListAPIView):
    """
    API view to list all language settings.
    Admin only access.
    """
    queryset = LanguageSetting.objects.all()
    serializer_class = LanguageSettingSerializer
    permission_classes = [IsAdminUser]


class EmailTemplateListCreateView(generics.ListCreateAPIView):
    """
    API view to list all email templates or create a new one.
    Admin only access.
    """
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [IsAdminUser]


class EmailTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update or delete an email template.
    Admin only access.
    """
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [IsAdminUser]
