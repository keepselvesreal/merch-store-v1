from rest_framework.views import APIView
import logging
from rest_framework.response import Response
from rest_framework import status
from .models import Order
from .serializers import OrderSerializer
from .permissions import IsOrderOwner
from django.db import transaction
from django.utils import timezone

class OrderCreateView(APIView):
    # permission_classes = [IsOrderOwner]
    permission_classes = []

    def post(self, request):
        user = request.user if request.user.is_authenticated else None
        session_id = request.headers.get('X-Session-ID')

        if not user and not session_id:
            return Response({"error": "User or session ID required"}, status=status.HTTP_401_UNAUTHORIZED)

        if not user and session_id:
            try:
                from django.contrib.sessions.models import Session
                Session.objects.get(session_key=session_id, expire_date__gt=timezone.now())
            except Session.DoesNotExist:
                return Response({"error": "Invalid or expired session ID"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            items_data = serializer.validated_data.get('items')
            total_price = 0

            with transaction.atomic():
                for item_data in items_data:
                    product_option = item_data['product_option']
                    quantity = item_data['quantity']
                    if product_option.stock < quantity:
                        return Response({"error": f"Insufficient stock for {product_option}"}, status=status.HTTP_400_BAD_REQUEST)
                    total_price += (product_option.product.price + product_option.additional_price) * quantity
                    product_option.stock -= quantity
                    product_option.save()

                serializer.validated_data['total_price'] = total_price
                serializer.validated_data['user'] = user
                serializer.validated_data['session_id'] = session_id if not user else None
                order = serializer.save()
                return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderListView(APIView):
    # permission_classes = [IsOrderOwner]
    permission_classes = []

    def get(self, request):
        user = request.user if request.user.is_authenticated else None
        session_id = request.headers.get('X-Session-ID')

        if not user and not session_id:
            return Response({"error": "User or session ID required"}, status=status.HTTP_401_UNAUTHORIZED)

        orders = Order.objects.filter(
            user=user if user else None,
            session_id=session_id if not user else None
        )
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class OrderDetailView(APIView):
    permission_classes = [] # 현재는 모든 접근 허용 (추후 필요시 IsOrderOwner 등 권한 클래스 추가)

    def get(self, request, order_number):
        try:
            if request.user.is_authenticated:
                # 인증된 사용자: order_number와 user가 일치하는 주문 조회
                order = Order.objects.get(order_number=order_number, user=request.user)
            else:
                # 비인증 사용자: order_number와 order_token이 일치하는 주문 조회
                order_token = request.headers.get('X-Order-Token') or request.query_params.get('order_token')
                if not order_token:
                    # 비인증 사용자는 order_token이 필수
                    return Response({"error": "Order token is required for guest users."},
                                    status=status.HTTP_401_UNAUTHORIZED) # 또는 403 Forbidden

                order = Order.objects.get(order_number=order_number, order_token=order_token)

            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({"error": "Order not found or access denied"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # 프로덕션 환경에서는 구체적인 오류 메시지 대신 일반적인 메시지를 반환하는 것이 좋습니다.
            logging.error(f"Unexpected error in OrderDetailView for order_number {order_number}: {str(e)}")
            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)