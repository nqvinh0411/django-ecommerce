from django.urls import path

from .views import (
    # Category views
    CategoryListView, CategoryCreateView, CategoryRetrieveUpdateDestroyView,
    # Brand views
    BrandListCreateView, BrandRetrieveUpdateDestroyView,
    # Tag views
    TagListCreateView, TagRetrieveUpdateDestroyView,
    # Attribute views
    AttributeListCreateView, AttributeRetrieveUpdateDestroyView,
    # AttributeValue views
    AttributeValueListCreateView, AttributeValueRetrieveUpdateDestroyView
)

app_name = 'catalog'

urlpatterns = [
    # Category endpoints
    # GET /categories - list all categories
    path('/categories', CategoryListView.as_view(), name='category-list'),
    # POST /categories - create a new category
    path('/categories/create', CategoryCreateView.as_view(), name='category-create'),
    # GET /categories/{slug} - retrieve a category
    path('/categories/<slug:slug>', CategoryRetrieveUpdateDestroyView.as_view(), name='category-detail'),
    # PUT/PATCH /categories/{slug} - update a category
    path('/categories/<slug:slug>/update', CategoryRetrieveUpdateDestroyView.as_view(), name='category-update'),
    # DELETE /categories/{slug} - delete a category
    path('/categories/<slug:slug>/delete', CategoryRetrieveUpdateDestroyView.as_view(), name='category-delete'),

    # Brand endpoints
    # GET /brands - list all brands
    path('/brands', BrandListCreateView.as_view(), name='brand-list'),
    # POST /brands - create a new brand
    path('/brands/create', BrandListCreateView.as_view(), name='brand-create'),
    # GET /brands/{slug} - retrieve a brand
    path('/brands/<slug:slug>', BrandRetrieveUpdateDestroyView.as_view(), name='brand-detail'),
    # PUT/PATCH /brands/{slug} - update a brand
    path('/brands/<slug:slug>/update', BrandRetrieveUpdateDestroyView.as_view(), name='brand-update'),
    # DELETE /brands/{slug} - delete a brand
    path('/brands/<slug:slug>/delete', BrandRetrieveUpdateDestroyView.as_view(), name='brand-delete'),

    # Tag endpoints
    # GET /tags - list all tags
    path('/tags', TagListCreateView.as_view(), name='tag-list'),
    # POST /tags - create a new tag
    path('/tags/create', TagListCreateView.as_view(), name='tag-create'),
    # GET /tags/{slug} - retrieve a tag
    path('/tags/<slug:slug>', TagRetrieveUpdateDestroyView.as_view(), name='tag-detail'),
    # PUT/PATCH /tags/{slug} - update a tag
    path('/tags/<slug:slug>/update', TagRetrieveUpdateDestroyView.as_view(), name='tag-update'),
    # DELETE /tags/{slug} - delete a tag
    path('/tags/<slug:slug>/delete', TagRetrieveUpdateDestroyView.as_view(), name='tag-delete'),

    # Attribute endpoints
    # GET /attributes - list all attributes
    path('/attributes', AttributeListCreateView.as_view(), name='attribute-list'),
    # POST /attributes - create a new attribute
    path('/attributes/create', AttributeListCreateView.as_view(), name='attribute-create'),
    # GET /attributes/{slug} - retrieve an attribute
    path('/attributes/<slug:slug>', AttributeRetrieveUpdateDestroyView.as_view(), name='attribute-detail'),
    # PUT/PATCH /attributes/{slug} - update an attribute
    path('/attributes/<slug:slug>/update', AttributeRetrieveUpdateDestroyView.as_view(), name='attribute-update'),
    # DELETE /attributes/{slug} - delete an attribute
    path('/attributes/<slug:slug>/delete', AttributeRetrieveUpdateDestroyView.as_view(), name='attribute-delete'),

    # AttributeValue endpoints
    # GET /attribute-values - list all attribute values
    path('/attribute-values', AttributeValueListCreateView.as_view(), name='attribute-value-list'),
    # POST /attribute-values - create a new attribute value
    path('/attribute-values/create', AttributeValueListCreateView.as_view(), name='attribute-value-create'),
    # GET /attribute-values/{slug} - retrieve an attribute value
    path('/attribute-values/<slug:slug>', AttributeValueRetrieveUpdateDestroyView.as_view(),
         name='attribute-value-detail'),
    # PUT/PATCH /attribute-values/{slug} - update an attribute value
    path('/attribute-values/<slug:slug>/update', AttributeValueRetrieveUpdateDestroyView.as_view(),
         name='attribute-value-update'),
    # DELETE /attribute-values/{slug} - delete an attribute value
    path('/attribute-values/<slug:slug>/delete', AttributeValueRetrieveUpdateDestroyView.as_view(),
         name='attribute-value-delete'),
]
