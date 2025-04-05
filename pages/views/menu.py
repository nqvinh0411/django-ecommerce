"""
Menu views module
"""
from rest_framework import generics

from ..models import MenuItem
from ..serializers import MenuItemSerializer
from ..permissions import IsAdminUserOrReadOnly


class MenuListCreateView(generics.ListCreateAPIView):
    """
    API view để liệt kê tất cả các menu item của một loại cụ thể hoặc tạo menu item mới.
    
    GET /menus/{menu_type} - Liệt kê menu items
    POST /menus/{menu_type} - Tạo menu item mới
    
    Admin có thể tạo menu items mới, trong khi bất kỳ ai cũng có thể xem menu items đang hoạt động.
    """
    serializer_class = MenuItemSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    
    def get_queryset(self):
        """
        Trả về menu items của loại được chỉ định.
        Đối với menu phân cấp, chỉ trả về các items gốc (parent=None).
        Các menu con sẽ được bao gồm trong output của serializer.
        """
        menu_type = self.kwargs.get('menu_type')
        
        # Start with base queryset
        queryset = MenuItem.objects.filter(menu_type=menu_type)
        
        # For hierarchical menus, only get root items in list view
        # Children will be included by the serializer
        queryset = queryset.filter(parent=None)
        
        # Non-admin users only see active items
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
            
        return queryset.order_by('order')
