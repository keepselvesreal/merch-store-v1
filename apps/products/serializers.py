from rest_framework import serializers
from .models import Product, ProductOption

class ProductOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOption
        fields = ['id', 'color', 'size', 'additional_price', 'stock']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'image', 'created_at', 'updated_at']

class ProductDetailSerializer(ProductSerializer):
    options = ProductOptionSerializer(many=True, read_only=True)

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ['options']