from rest_framework import serializers
from .models import Cart, CartItem
from apps.products.models import ProductOption
from apps.products.serializers import ProductOptionSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product_option = ProductOptionSerializer(read_only=True)
    product_option_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductOption.objects.all(), source='product_option', write_only=True
    )

    class Meta:
        model = CartItem
        fields = ['id', 'product_option', 'product_option_id', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'session_id', 'created_at', 'items']