from django.urls import path
from .views import (
    # Category views
    CategoryListCreateView, CategoryRetrieveUpdateDestroyView,
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
    # POST /categories - create a new category
    path('categories', CategoryListCreateView.as_view(), name='category-list-create'),
    
    # GET /categories/{slug} - retrieve a category
    # PUT/PATCH /categories/{slug} - update a category
    # DELETE /categories/{slug} - delete a category
    path('categories/<slug:slug>', CategoryRetrieveUpdateDestroyView.as_view(), name='category-detail'),
    
    # Brand endpoints
    # GET /brands - list all brands
    # POST /brands - create a new brand
    path('brands', BrandListCreateView.as_view(), name='brand-list-create'),
    
    # GET /brands/{slug} - retrieve a brand
    # PUT/PATCH /brands/{slug} - update a brand
    # DELETE /brands/{slug} - delete a brand
    path('brands/<slug:slug>', BrandRetrieveUpdateDestroyView.as_view(), name='brand-detail'),
    
    # Tag endpoints
    # GET /tags - list all tags
    # POST /tags - create a new tag
    path('tags', TagListCreateView.as_view(), name='tag-list-create'),
    
    # GET /tags/{slug} - retrieve a tag
    # PUT/PATCH /tags/{slug} - update a tag
    # DELETE /tags/{slug} - delete a tag
    path('tags/<slug:slug>', TagRetrieveUpdateDestroyView.as_view(), name='tag-detail'),
    
    # Attribute endpoints
    # GET /attributes - list all attributes
    # POST /attributes - create a new attribute
    path('attributes', AttributeListCreateView.as_view(), name='attribute-list-create'),
    
    # GET /attributes/{slug} - retrieve an attribute
    # PUT/PATCH /attributes/{slug} - update an attribute
    # DELETE /attributes/{slug} - delete an attribute
    path('attributes/<slug:slug>', AttributeRetrieveUpdateDestroyView.as_view(), name='attribute-detail'),
    
    # AttributeValue endpoints
    # GET /attribute-values - list all attribute values
    # POST /attribute-values - create a new attribute value
    path('attribute-values', AttributeValueListCreateView.as_view(), name='attribute-value-list-create'),
    
    # GET /attribute-values/{slug} - retrieve an attribute value
    # PUT/PATCH /attribute-values/{slug} - update an attribute value
    # DELETE /attribute-values/{slug} - delete an attribute value
    path('attribute-values/<slug:slug>', AttributeValueRetrieveUpdateDestroyView.as_view(), name='attribute-value-detail'),
]
