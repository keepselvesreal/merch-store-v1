from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.sessions.models import Session
from django.utils import timezone
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer

class CartView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # 회원: JWT로 사용자 확인
        user = request.user if request.user.is_authenticated else None
        session_id = request.headers.get('X-Session-ID')

        if not user and not session_id:
            return Response({"error": "User or session ID required"}, status=status.HTTP_401_UNAUTHORIZED)

        # 비회원: 세션 ID 검증
        if not user and session_id:
            try:
                Session.objects.get(session_key=session_id, expire_date__gt=timezone.now())
            except Session.DoesNotExist:
                return Response({"error": "Invalid or expired session ID"}, status=status.HTTP_401_UNAUTHORIZED)

        # 장바구니 조회
        cart, created = Cart.objects.get_or_create(
            user=user if user else None,
            session_id=session_id if not user else None
        )
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CartItemView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user = request.user if request.user.is_authenticated else None
        session_id = request.headers.get('X-Session-ID')

        if not user and not session_id:
            return Response({"error": "User or session ID required"}, status=status.HTTP_401_UNAUTHORIZED)

        if not user and session_id:
            try:
                Session.objects.get(session_key=session_id, expire_date__gt=timezone.now())
            except Session.DoesNotExist:
                return Response({"error": "Invalid or expired session ID"}, status=status.HTTP_401_UNAUTHORIZED)

        cart, created = Cart.objects.get_or_create(
            user=user if user else None,
            session_id=session_id if not user else None
        )

        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            product_option = serializer.validated_data['product_option']
            quantity = serializer.validated_data['quantity']

            # 재고 확인
            if product_option.stock < quantity:
                return Response({"error": "Insufficient stock"}, status=status.HTTP_400_BAD_REQUEST)

            # 기존 항목 확인
            cart_item, item_created = CartItem.objects.get_or_create(
                cart=cart,
                product_option=product_option,
                defaults={'quantity': quantity}
            )
            if not item_created:
                cart_item.quantity += quantity
                if product_option.stock < cart_item.quantity:
                    return Response({"error": "Insufficient stock"}, status=status.HTTP_400_BAD_REQUEST)
                cart_item.save()

            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CartItemDetailView(APIView):
    permission_classes = [AllowAny]

    def patch(self, request, item_id):
        user = request.user if request.user.is_authenticated else None
        session_id = request.headers.get('X-Session-ID')

        if not user and not session_id:
            return Response({"error": "User or session ID required"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            cart = Cart.objects.get(
                user=user if user else None,
                session_id=session_id if not user else None
            )
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CartItemSerializer(cart_item, data=request.data, partial=True)
        if serializer.is_valid():
            quantity = serializer.validated_data.get('quantity', cart_item.quantity)
            if cart_item.product_option.stock < quantity:
                return Response({"error": "Insufficient stock"}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, item_id):
        user = request.user if request.user.is_authenticated else None
        session_id = request.headers.get('X-Session-ID')

        if not user and not session_id:
            return Response({"error": "User or session ID required"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            cart = Cart.objects.get(
                user=user if user else None,
                session_id=session_id if not user else None
            )
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)