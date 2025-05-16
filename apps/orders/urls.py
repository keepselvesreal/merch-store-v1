from django.urls import path
from .views import OrderCreateView, OrderListView, OrderDetailView, OrderPayView

urlpatterns = [
    path('', OrderCreateView.as_view(), name='order-create'),
    path('list/', OrderListView.as_view(), name='order-list'),
    path('<str:order_number>/', OrderDetailView.as_view(), name='order-detail'),
    path('<str:order_number>/pay/', OrderPayView.as_view(), name='order-pay'),
]