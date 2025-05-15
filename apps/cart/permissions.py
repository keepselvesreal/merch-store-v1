from rest_framework.permissions import BasePermission
from .models import Cart
from django.contrib.sessions.models import Session
from django.utils import timezone

class IsCartOwner(BasePermission):
    def has_permission(self, request, view):
        user = request.user if request.user.is_authenticated else None
        session_id = request.headers.get('X-Session-ID')

        # 회원 또는 세션 ID 필수
        if not user and not session_id:
            return False

        # 비회원: 세션 ID 유효성 확인
        if not user and session_id:
            try:
                Session.objects.get(session_key=session_id, expire_date__gt=timezone.now())
            except Session.DoesNotExist:
                return False

        # 장바구니 소유자 확인
        try:
            cart = Cart.objects.get(
                user=user if user else None,
                session_id=session_id if not user else None
            )
            return True
        except Cart.DoesNotExist:
            return False