from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order, Payment
from .serializers import OrderSerializer, PaymentSerializer
from .permissions import IsOrderOwner
from apps.products.models import ProductOption
from django.db import transaction
from django.utils import timezone
import logging
import uuid

logger = logging.getLogger(__name__)

class OrderCreateView(APIView):
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
    permission_classes = []

    def get(self, request, order_number):
        try:
            if request.user.is_authenticated:
                order = Order.objects.get(order_number=order_number, user=request.user)
            else:
                order_token = request.headers.get('X-Order-Token') or request.query_params.get('order_token')
                if not order_token:
                    return Response({"error": "Order token is required for guest users."},
                                    status=status.HTTP_401_UNAUTHORIZED)
                order = Order.objects.get(order_number=order_number, order_token=order_token)

            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({"error": "Order not found or access denied"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Unexpected error in OrderDetailView for order_number {order_number}: {str(e)}")
            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class OrderPayView(APIView):
    permission_classes = [IsOrderOwner]

    def post(self, request, order_number):
        user = request.user if request.user.is_authenticated else None
        session_id = request.headers.get('X-Session-ID')
        order_token = request.headers.get('X-Order-Token')

        try:
            # 소유자 검증
            order = Order.objects.get(
                order_number=order_number,
                user=user if user else None,
                session_id=session_id if not user else None,
                order_token=order_token if not user else None
            )
        except Order.DoesNotExist:
            return Response({"error": "Order not found or access denied"}, status=status.HTTP_404_NOT_FOUND)

        if order.payment_status != 'pending':
            return Response({"error": f"Order payment status is {order.payment_status}"}, status=status.HTTP_400_BAD_REQUEST)

        # 결제 데이터 검증
        serializer = PaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # 외부 결제 서비스 호출 (예: 가정된 호출)
                payment_method_id = request.data.get('payment_method_id')
                # 실제 결제 서비스 SDK로 대체 (예: KakaoPay, TossPayments)
                # payment_response = external_payment_service.process_payment(
                #     amount=order.total_price,
                #     payment_method_id=payment_method_id,
                #     order_id=order.order_number
                # )

                # 시뮬레이션: 결제 성공 가정
                payment_id = f"pay_{uuid.uuid4()}"  # 결제 서비스에서 제공하는 ID
                payment_status = 'completed'  # 결제 서비스 응답 기반

                # 결제 정보 저장
                payment, created = Payment.objects.get_or_create(
                    order=order,
                    defaults={
                        'payment_id': payment_id,
                        'amount': order.total_price,
                        'status': payment_status
                    }
                )

                if payment_status == 'completed':
                    order.payment_status = 'completed'
                    order.status = 'completed'
                    order.save()
                    logger.info(f"Payment succeeded for order {order.order_number}, payment_id: {payment_id}")
                    return Response({
                        'payment': PaymentSerializer(payment).data,
                        'order': OrderSerializer(order).data
                    }, status=status.HTTP_200_OK)
                else:
                    payment.status = 'failed'
                    payment.save()
                    order.payment_status = 'failed'
                    order.save()
                    logger.warning(f"Payment failed for order {order.order_number}, payment_id: {payment_id}")
                    return Response({"error": "Payment failed"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Payment error for order {order.order_number}: {str(e)}")
            return Response({"error": f"Payment error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)