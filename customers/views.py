from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateDestroyAPIView,
    ListAPIView, RetrieveAPIView
)
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Customer, CustomerGroup, CustomerAddress, CustomerActivity
from .serializers import (
    CustomerSerializer, CustomerGroupSerializer,
    CustomerAddressSerializer, CustomerActivitySerializer
)
from .permissions import IsCustomerOwner, IsAdminOrReadOnly


# Customer views
class CustomerListCreateView(ListCreateAPIView):
    """
    API endpoint for listing all customers or creating a new customer.
    """
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomerOwner]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Customer.objects.all()
        return Customer.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CustomerRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating or deleting a customer.
    """
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomerOwner]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Customer.objects.all()
        return Customer.objects.filter(user=self.request.user)


# CustomerGroup views
class CustomerGroupListCreateView(ListCreateAPIView):
    """
    API endpoint for listing all customer groups or creating a new customer group.
    """
    queryset = CustomerGroup.objects.all()
    serializer_class = CustomerGroupSerializer
    permission_classes = [IsAdminOrReadOnly]


class CustomerGroupRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating or deleting a customer group.
    """
    queryset = CustomerGroup.objects.all()
    serializer_class = CustomerGroupSerializer
    permission_classes = [IsAdminOrReadOnly]


# CustomerAddress views
class CustomerAddressListCreateView(ListCreateAPIView):
    """
    API endpoint for listing all customer addresses or creating a new customer address.
    """
    serializer_class = CustomerAddressSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomerOwner]

    def get_queryset(self):
        return CustomerAddress.objects.filter(customer__user=self.request.user)

    def perform_create(self, serializer):
        customer = get_object_or_404(Customer, user=self.request.user)
        serializer.save(customer=customer)


class CustomerAddressRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating or deleting a customer address.
    """
    serializer_class = CustomerAddressSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomerOwner]

    def get_queryset(self):
        return CustomerAddress.objects.filter(customer__user=self.request.user)


class CustomerAddressDefaultShippingView(APIView):
    """
    API endpoint for retrieving the default shipping address.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        address = CustomerAddress.objects.filter(
            customer__user=request.user,
            is_default=True,
            address_type__in=['shipping', 'both']
        ).first()
        if address:
            serializer = CustomerAddressSerializer(address)
            return Response(serializer.data)
        return Response({'detail': 'No default shipping address found.'}, status=status.HTTP_404_NOT_FOUND)


class CustomerAddressDefaultBillingView(APIView):
    """
    API endpoint for retrieving the default billing address.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        address = CustomerAddress.objects.filter(
            customer__user=request.user,
            is_default=True,
            address_type__in=['billing', 'both']
        ).first()
        if address:
            serializer = CustomerAddressSerializer(address)
            return Response(serializer.data)
        return Response({'detail': 'No default billing address found.'}, status=status.HTTP_404_NOT_FOUND)


# CustomerActivity views
class CustomerActivityListView(ListAPIView):
    """
    API endpoint for listing all customer activities.
    """
    serializer_class = CustomerActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return CustomerActivity.objects.all()
        return CustomerActivity.objects.filter(customer__user=self.request.user)


class CustomerActivityRetrieveView(RetrieveAPIView):
    """
    API endpoint for retrieving a customer activity.
    """
    serializer_class = CustomerActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return CustomerActivity.objects.all()
        return CustomerActivity.objects.filter(customer__user=self.request.user)