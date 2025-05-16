from rest_framework.permissions import BasePermission
from .models import Order
from django.contrib.sessions.models import Session
from django.utils import timezone

class IsOrderOwner(BasePermission):
    def has_permission(self, request, view):
        user = request.user if request.user.is_authenticated else None
        session_id = request.headers.get('X-Session-ID')
        order_token = request.headers.get('X-Order-Token') or request.query_params.get('order_token')

        if not user and not (session_id or order_token):
            return False

        if not user and session_id:
            try:
                Session.objects.get(session_key=session_id, expire_date__gt=timezone.now())
            except Session.DoesNotExist:
                return False

        try:
            order = Order.objects.get(
                user=user if user else None,
                session_id=session_id if not user else None,
                order_token=order_token if not user else None
            )
            return True
        except Order.DoesNotExist:
            return False