from django.db import models
from apps.accounts.models import User
from apps.products.models import ProductOption

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # 회원
    session_id = models.CharField(max_length=100, null=True, blank=True, db_index=True)  # 비회원 세션 ID
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시간

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(user__isnull=False) | models.Q(session_id__isnull=False),
                name='cart_user_or_session_required'  # 사용자 또는 세션 ID 필수
            )
        ]

    def __str__(self):
        return f"Cart {self.id} - {'User' if self.user else 'Guest'}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')  # 장바구니
    product_option = models.ForeignKey(ProductOption, on_delete=models.CASCADE)  # 상품 옵션
    quantity = models.PositiveIntegerField()  # 수량

    def __str__(self):
        return f"{self.product_option} x {self.quantity}"