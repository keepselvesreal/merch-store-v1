from django.urls import path
from .views import ProductListView, ProductDetailView, ProductOptionListView

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('<int:id>/', ProductDetailView.as_view(), name='product_detail'),
    path('<int:id>/options/', ProductOptionListView.as_view(), name='product_options'),
]
