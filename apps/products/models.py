from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200)  # 상품 이름
    description = models.TextField()  # 상품 설명
    price = models.DecimalField(max_digits=10, decimal_places=2)  # 가격
    stock = models.PositiveIntegerField()  # 재고
    image = models.ImageField(upload_to='product_images/', blank=True)  # 상품 이미지
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시간
    updated_at = models.DateTimeField(auto_now=True)  # 수정 시간

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'products'

class ProductOption(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='options')  # 상품 참조
    color = models.CharField(max_length=50)  # 색상
    size = models.CharField(max_length=50)  # 사이즈
    additional_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # 추가 가격
    stock = models.PositiveIntegerField()  # 옵션별 재고

    def __str__(self):
        return f"{self.product.name} - {self.color}/{self.size}"

    class Meta:
        app_label = 'products'
