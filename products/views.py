from core.permissions.base import IsOwnerOrReadOnly, IsAdminOrReadOnly
from core.views.base import (
    BaseListCreateView, BaseRetrieveView,
    BaseUpdateView, BaseDestroyView, BaseCreateView, BaseListView
)
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Product
from .serializers import ProductSerializer, ProductCreateSerializer, ProductImageSerializer


class ProductListView(BaseListView):
    queryset = Product.objects.order_by('id').all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ['category', 'seller_id']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'stock']


class ProductCreateView(BaseCreateView):
    queryset = Product.objects.all()
    serializer_class = ProductCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


class ProductRetrieveView(BaseRetrieveView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]


class ProductUpdateView(BaseUpdateView):
    queryset = Product.objects.all()
    serializer_class = ProductCreateSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user)


class ProductDestroyView(BaseDestroyView):
    queryset = Product.objects.all()
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user)


class ProductImageUploadView(BaseCreateView):
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        product_id = self.kwargs.get("product_id")
        product = get_object_or_404(Product, id=product_id, seller=self.request.user)
        serializer.save(product=product)
