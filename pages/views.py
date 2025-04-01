from rest_framework import generics, status, filters
from rest_framework.permissions import IsAdminUser, AllowAny
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from .models import Page, Banner, MenuItem
from .serializers import PageSerializer, BannerSerializer, MenuItemSerializer
from .permissions import IsAdminUserOrReadOnly


class PageListView(generics.ListCreateAPIView):
    """
    API view to list all pages or create a new page.
    Admin users can create, while anyone can view published pages.
    """
    serializer_class = PageSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_published']
    search_fields = ['title', 'slug', 'content_text']
    
    def get_queryset(self):
        """
        Return all pages for admin users, but only published 
        pages for non-admin users.
        """
        queryset = Page.objects.all()
        
        # Non-admin users only see published pages
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                is_published=True,
                published_at__lte=timezone.now()
            )
            
        return queryset


class PageDetailBySlugView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update or delete a page by slug.
    Admin users can update/delete, while anyone can view published pages.
    """
    serializer_class = PageSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    lookup_field = 'slug'
    
    def get_queryset(self):
        """
        Return all pages for admin users, but only published 
        pages for non-admin users.
        """
        queryset = Page.objects.all()
        
        # Non-admin users only see published pages
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                is_published=True,
                published_at__lte=timezone.now()
            )
            
        return queryset


class BannerListView(generics.ListCreateAPIView):
    """
    API view to list all banners or create a new banner.
    Admin users can create, while anyone can view active banners.
    Supports filtering by position.
    """
    serializer_class = BannerSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['position', 'is_active']
    
    def get_queryset(self):
        """
        Return all banners for admin users, but only active and 
        non-expired banners for non-admin users.
        Optional query parameter for position.
        """
        queryset = Banner.objects.all()
        
        # Non-admin users only see active, non-expired banners
        if not self.request.user.is_staff:
            now = timezone.now()
            queryset = queryset.filter(
                is_active=True,
                start_date__lte=now
            ).filter(
                end_date__isnull=True
            ) | queryset.filter(
                is_active=True,
                start_date__lte=now,
                end_date__gt=now
            )
        
        # Filter by position if provided in URL params
        position = self.request.query_params.get('position', None)
        if position:
            queryset = queryset.filter(position=position)
            
        return queryset


class MenuListView(generics.ListCreateAPIView):
    """
    API view to list all menu items of a specific type or create a new menu item.
    Admin users can create, while anyone can view active menu items.
    """
    serializer_class = MenuItemSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    
    def get_queryset(self):
        """
        Return menu items of the specified type.
        For hierarchical menus, only return root items (parent=None).
        Children will be included in the serializer output.
        """
        menu_type = self.kwargs.get('menu_type')
        queryset = MenuItem.objects.filter(menu_type=menu_type, parent__isnull=True)
        
        # Non-admin users only see active menu items
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
            
        return queryset.order_by('order')
