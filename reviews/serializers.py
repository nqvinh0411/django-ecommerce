from products.serializers import ProductSerializer
from rest_framework import serializers
from users.serializers import UserSerializer

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Review.objects.all(), source='product', write_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'product', 'product_id', 'rating', 'comment', 'created_at']
