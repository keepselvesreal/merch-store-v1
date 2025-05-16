from rest_framework import serializers
from .models import Order, OrderItem, Payment
from apps.products.serializers import ProductOptionSerializer
from apps.products.models import ProductOption

class OrderItemSerializer(serializers.ModelSerializer):
    product_option = ProductOptionSerializer(read_only=True)
    product_option_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductOption.objects.all(), source='product_option', write_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'product_option', 'product_option_id', 'quantity', 'price']

    def validate(self, data):
        product_option = data.get('product_option')
        price = data.get('price')
        expected_price = product_option.product.price + product_option.additional_price
        if price != expected_price:
            raise serializers.ValidationError({"price": f"Expected price is {expected_price}"})
        return data

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'payment_id', 'amount', 'status', 'created_at', 'updated_at']
        read_only_fields = ['payment_id', 'amount', 'status', 'created_at', 'updated_at']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    items_data = serializers.ListField(child=OrderItemSerializer(), write_only=True, source='items')
    payment = PaymentSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'session_id', 'order_number', 'order_token', 'buyer_name', 'buyer_email',
            'buyer_phone', 'recipient_name', 'recipient_phone', 'shipping_address', 'status',
            'payment_status', 'total_price', 'payment_method', 'cash_receipt_type',
            'cash_receipt_number', 'created_at', 'updated_at', 'items', 'items_data', 'payment'
        ]
        read_only_fields = ['order_number', 'order_token', 'total_price', 'payment_status', 'created_at', 'updated_at']

    def validate_items_data(self, value):
        if not value:
            raise serializers.ValidationError("At least one item is required.")
        return value

    def create(self, validated_data):
        import uuid
        items_data = validated_data.pop('items')
        validated_data['order_number'] = str(uuid.uuid4())[:8].upper()
        validated_data['order_token'] = str(uuid.uuid4())
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        return order