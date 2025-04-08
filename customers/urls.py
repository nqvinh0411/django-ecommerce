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
    path('', CustomerListCreateView.as_view(), name='customer-list'),
    # POST /customers - create a new customer
    path('/create', CustomerListCreateView.as_view(), name='customer-create'),
    # GET /customers/{id} - retrieve a customer
    path('/<int:pk>', CustomerRetrieveUpdateDestroyView.as_view(), name='customer-detail'),
    # PUT/PATCH /customers/{id} - update a customer
    path('/<int:pk>/update', CustomerRetrieveUpdateDestroyView.as_view(), name='customer-update'),
    # DELETE /customers/{id} - delete a customer
    path('/<int:pk>/delete', CustomerRetrieveUpdateDestroyView.as_view(), name='customer-delete'),

    # CustomerGroup endpoints
    # GET /groups - list all customer groups
    path('/groups', CustomerGroupListCreateView.as_view(), name='customer-group-list-create'),
    # POST /groups - create a new customer group
    path('/groups/create', CustomerGroupListCreateView.as_view(), name='customer-group-list-create'),
    # GET /groups/{id} - retrieve a customer group
    path('/groups/<int:pk>', CustomerGroupRetrieveUpdateDestroyView.as_view(), name='customer-group-detail'),
    # PUT/PATCH /groups/{id} - update a customer group
    path('/groups/<int:pk>/update', CustomerGroupRetrieveUpdateDestroyView.as_view(), name='customer-group-update'),
    # DELETE /groups/{id} - delete a customer group
    path('/groups/<int:pk>/delete', CustomerGroupRetrieveUpdateDestroyView.as_view(), name='customer-group-delete'),

    # CustomerAddress endpoints
    # GET /addresses - list all customer addresses
    path('/addresses', CustomerAddressListCreateView.as_view(), name='customer-address-list-create'),
    # POST /addresses - create a new customer address
    path('/addresses/create', CustomerAddressListCreateView.as_view(), name='customer-address-list-create'),
    # GET /addresses/{id} - retrieve a customer address
    path('/addresses/<int:pk>', CustomerAddressRetrieveUpdateDestroyView.as_view(), name='customer-address-detail'),
    # PUT/PATCH /addresses/{id} - update a customer address
    path('/addresses/<int:pk>/update', CustomerAddressRetrieveUpdateDestroyView.as_view(),
         name='customer-address-update'),
    # DELETE /addresses/{id} - delete a customer address
    path('/addresses/<int:pk>/delete', CustomerAddressRetrieveUpdateDestroyView.as_view(),
         name='customer-address-delete'),
    # GET /addresses/default-shipping - get the default shipping address
    path('/addresses/default-shipping', CustomerAddressDefaultShippingView.as_view(),
         name='customer-address-default-shipping'),
    # GET /addresses/default-billing - get the default billing address
    path('/addresses/default-billing', CustomerAddressDefaultBillingView.as_view(),
         name='customer-address-default-billing'),

    # CustomerActivity endpoints
    # GET /activities - list all customer activities
    path('/activities', CustomerActivityListView.as_view(), name='customer-activity-list'),
    # GET /activities/{id} - retrieve a customer activity
    path('/activities/<int:pk>', CustomerActivityRetrieveView.as_view(), name='customer-activity-detail'),
]
