from django.urls import path
from .views import ProductListView, ProductDetailView, ProductOptionListView

urlpatterns = [
    path('', ProductListView.as_view(), name='product-list'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('<int:pk>/options/', ProductOptionListView.as_view(), name='product-options'),
]