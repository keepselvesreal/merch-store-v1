from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import (
    UserSerializer,
    CustomTokenObtainPairSerializer,
    GuestSessionSerializer,
    AuthCheckSerializer
)
from django.contrib.sessions.models import Session
from django.utils import timezone


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class GuestSessionView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Django 세션 키 생성 및 저장
        request.session['initiated'] = True
        request.session.save()
        session_key = request.session.session_key
        # 응답으로 세션 키 전달
        serializer = GuestSessionSerializer(instance={'session_id': session_key})
        return Response(serializer.data, status=status.HTTP_200_OK)

class CustomTokenRefreshView(TokenRefreshView):
    # 일반적으로 별도의 커스터마이징이 필요 없지만,
    # 필요하다면 여기서 serializer_class 등을 오버라이드할 수 있습니다.
    pass

class AuthCheckView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        session_key = request.headers.get('X-Session-ID')
        user = request.user if request.user.is_authenticated else None

        # 인증된 사용자 처리
        if user:
            data = {'is_authenticated': True, 'session_id': None, 'user': user}
            serializer = AuthCheckSerializer(instance=data)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # 게스트 세션 처리: 헤더에 session_key 필수
        if not session_key:
            return Response({'error': 'Session ID is required'}, status=status.HTTP_401_UNAUTHORIZED)
        from django.contrib.sessions.backends.db import SessionStore
        store = SessionStore(session_key=session_key)
        try:
            session_data = store.load()
        except Exception:
            return Response({'error': 'Invalid or expired session ID'}, status=status.HTTP_401_UNAUTHORIZED)
        if not session_data.get('initiated'):
            return Response({'error': 'Invalid or expired session ID'}, status=status.HTTP_401_UNAUTHORIZED)

        data = {'is_authenticated': False, 'session_id': session_key, 'user': None}
        serializer = AuthCheckSerializer(instance=data)
        return Response(serializer.data, status=status.HTTP_200_OK)