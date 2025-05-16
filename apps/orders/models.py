from django.db import models
from apps.accounts.models import User
from apps.products.models import ProductOption

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    )
    PAYMENT_METHODS = (
        ('card', 'Credit Card'),
        ('bank', 'Bank Transfer'),
    )
    CASH_RECEIPT_TYPES = (
        ('personal', 'Personal'),
        ('business', 'Business'),
        ('none', 'None'),
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    order_number = models.CharField(max_length=50, unique=True, db_index=True)
    order_token = models.CharField(max_length=100, unique=True, null=True, blank=True, db_index=True)  # 비회원 조회용
    buyer_name = models.CharField(max_length=100, null=True, blank=True)
    buyer_email = models.EmailField(null=True, blank=True, db_index=True)
    buyer_phone = models.CharField(max_length=15, null=True, blank=True, db_index=True)
    recipient_name = models.CharField(max_length=100, null=True, blank=True)
    recipient_phone = models.CharField(max_length=15, null=True, blank=True)
    shipping_address = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    cash_receipt_type = models.CharField(max_length=20, choices=CASH_RECEIPT_TYPES, default='none')
    cash_receipt_number = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(user__isnull=False) | models.Q(session_id__isnull=False),
                name='order_user_or_session_required'
            )
        ]

    def __str__(self):
        return f"Order {self.order_number} - {'User' if self.user else 'Guest'}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_option = models.ForeignKey(ProductOption, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_option} x {self.quantity}"