from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from products.models import Product, Category, ProductImage
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class ProductTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="seller", password="password", is_seller=True)
        self.category = Category.objects.create(name="Electronics", slug="electronics")
        self.client.force_authenticate(user=self.user)

    def test_create_product(self):
        """Test tạo sản phẩm mới"""
        data = {
            "name": "Laptop",
            "description": "Gaming Laptop",
            "price": 1200,
            "category": self.category.id,
            "stock": 10
        }
        response = self.client.post("/api/products/create", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['data']['name'], 'Laptop')

    def test_create_product_without_authentication(self):
        """Test tạo sản phẩm khi chưa đăng nhập"""
        self.client.logout()
        data = {"name": "Laptop", "description": "Gaming Laptop", "price": 1200, "category": self.category.id, "stock": 10}
        response = self.client.post("/api/products/create", data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['status'], 'error')

    def test_get_products(self):
        """Test lấy danh sách sản phẩm"""
        # Tạo vài sản phẩm để test
        Product.objects.create(name="Test Laptop 1", description="Test model 1", 
                              price=1000, category=self.category, seller=self.user)
        Product.objects.create(name="Test Laptop 2", description="Test model 2", 
                              price=1200, category=self.category, seller=self.user)
                              
        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        # Kiểm tra xem danh sách sản phẩm có chứa đúng số lượng sản phẩm đã tạo
        self.assertEqual(len(response.data['data']), 2)

    def test_get_product_detail(self):
        """Test xem chi tiết sản phẩm"""
        product = Product.objects.create(name="Detail Laptop", description="Good specs", 
                                        price=1500, category=self.category, seller=self.user)
        response = self.client.get(f"/api/products/{product.id}/view")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['data']['name'], "Detail Laptop")

    def test_update_product(self):
        """Test cập nhật sản phẩm"""
        product = Product.objects.create(name="Old Laptop", description="Old model", 
                                        price=1000, category=self.category, seller=self.user)
        data = {"name": "Updated Laptop", "description": "Old model", "price": 1400, 
               "category": self.category.id, "stock": 8}
        response = self.client.put(f"/api/products/{product.id}/update", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['data']['name'], "Updated Laptop")
        self.assertEqual(response.data['data']['price'], 1400)

    def test_delete_product(self):
        """Test xóa sản phẩm"""
        product = Product.objects.create(name="Delete Laptop", description="To be deleted", 
                                        price=1000, category=self.category, seller=self.user)
        response = self.client.delete(f"/api/products/{product.id}/delete")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['status'], 'success')
        # Kiểm tra xem sản phẩm có bị xóa thật không
        self.assertEqual(Product.objects.filter(id=product.id).count(), 0)

    def test_upload_product_image(self):
        """Test upload ảnh sản phẩm"""
        product = Product.objects.create(name="Image Laptop", description="With image", 
                                       price=1000, category=self.category, seller=self.user)
        # Tạo một file ảnh giả cho việc test
        image_content = b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
        image = SimpleUploadedFile("test_image.gif", image_content, content_type="image/gif")
        
        data = {
            "product": product.id,
            "image": image,
            "is_primary": True,
            "alt_text": "Test image"
        }
        response = self.client.post(f"/api/products/{product.id}/images/upload", data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
        
        # Kiểm tra xem ảnh có được thêm vào sản phẩm không
        self.assertEqual(ProductImage.objects.filter(product=product).count(), 1)
