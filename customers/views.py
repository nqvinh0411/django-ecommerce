from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Customer, CustomerGroup, CustomerAddress, CustomerActivity
from .serializers import (
    CustomerSerializer, CustomerGroupSerializer,
    CustomerAddressSerializer, CustomerActivitySerializer
)
from .permissions import IsCustomerOwner, IsAdminOrReadOnly

class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomerOwner]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Customer.objects.all()
        return Customer.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CustomerGroupViewSet(viewsets.ModelViewSet):
    queryset = CustomerGroup.objects.all()
    serializer_class = CustomerGroupSerializer
    permission_classes = [IsAdminOrReadOnly]

class CustomerAddressViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerAddressSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomerOwner]

    def get_queryset(self):
        return CustomerAddress.objects.filter(customer__user=self.request.user)

    def perform_create(self, serializer):
        customer = get_object_or_404(Customer, user=self.request.user)
        serializer.save(customer=customer)

    @action(detail=False, methods=['get'])
    def default_shipping(self, request):
        address = self.get_queryset().filter(
            is_default=True,
            address_type__in=['shipping', 'both']
        ).first()
        if address:
            serializer = self.get_serializer(address)
            return Response(serializer.data)
        return Response({'detail': 'No default shipping address found.'}, status=404)

    @action(detail=False, methods=['get'])
    def default_billing(self, request):
        address = self.get_queryset().filter(
            is_default=True,
            address_type__in=['billing', 'both']
        ).first()
        if address:
            serializer = self.get_serializer(address)
            return Response(serializer.data)
        return Response({'detail': 'No default billing address found.'}, status=404)

class CustomerActivityViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CustomerActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return CustomerActivity.objects.all()
        return CustomerActivity.objects.filter(customer__user=self.request.user)