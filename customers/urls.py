from django.urls import path
from .views import (
    # Customer views
    CustomerListCreateView, CustomerRetrieveUpdateDestroyView,
    # CustomerGroup views
    CustomerGroupListCreateView, CustomerGroupRetrieveUpdateDestroyView,
    # CustomerAddress views
    CustomerAddressListCreateView, CustomerAddressRetrieveUpdateDestroyView,
    CustomerAddressDefaultShippingView, CustomerAddressDefaultBillingView,
    # CustomerActivity views
    CustomerActivityListView, CustomerActivityRetrieveView
)

app_name = 'customers'

urlpatterns = [
    # Customer endpoints
    # GET /customers - list all customers
    # POST /customers - create a new customer
    path('customers', CustomerListCreateView.as_view(), name='customer-list-create'),
    
    # GET /customers/{id} - retrieve a customer
    # PUT/PATCH /customers/{id} - update a customer
    # DELETE /customers/{id} - delete a customer
    path('customers/<int:pk>', CustomerRetrieveUpdateDestroyView.as_view(), name='customer-detail'),
    
    # CustomerGroup endpoints
    # GET /groups - list all customer groups
    # POST /groups - create a new customer group
    path('groups', CustomerGroupListCreateView.as_view(), name='customer-group-list-create'),
    
    # GET /groups/{id} - retrieve a customer group
    # PUT/PATCH /groups/{id} - update a customer group
    # DELETE /groups/{id} - delete a customer group
    path('groups/<int:pk>', CustomerGroupRetrieveUpdateDestroyView.as_view(), name='customer-group-detail'),
    
    # CustomerAddress endpoints
    # GET /addresses - list all customer addresses
    # POST /addresses - create a new customer address
    path('addresses', CustomerAddressListCreateView.as_view(), name='customer-address-list-create'),
    
    # GET /addresses/{id} - retrieve a customer address
    # PUT/PATCH /addresses/{id} - update a customer address
    # DELETE /addresses/{id} - delete a customer address
    path('addresses/<int:pk>', CustomerAddressRetrieveUpdateDestroyView.as_view(), name='customer-address-detail'),
    
    # GET /addresses/default-shipping - get the default shipping address
    path('addresses/default-shipping', CustomerAddressDefaultShippingView.as_view(), name='customer-address-default-shipping'),
    
    # GET /addresses/default-billing - get the default billing address
    path('addresses/default-billing', CustomerAddressDefaultBillingView.as_view(), name='customer-address-default-billing'),
    
    # CustomerActivity endpoints
    # GET /activities - list all customer activities
    path('activities', CustomerActivityListView.as_view(), name='customer-activity-list'),
    
    # GET /activities/{id} - retrieve a customer activity
    path('activities/<int:pk>', CustomerActivityRetrieveView.as_view(), name='customer-activity-detail'),
]
