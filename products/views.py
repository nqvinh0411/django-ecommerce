from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer, ProductCreateSerializer, ProductImageSerializer


class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]


class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]


class ProductUpdateView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user)


class ProductDeleteView(generics.DestroyAPIView):
    queryset = Product.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user)


class ProductImageUploadView(generics.CreateAPIView):
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        product_id = self.kwargs.get("product_id")
        product = Product.objects.get(id=product_id, seller=self.request.user)
        serializer.save(product=product)
