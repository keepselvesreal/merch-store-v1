from django.urls import path
from .views import RegisterView, CustomTokenObtainPairView, GuestSessionView, AuthCheckView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    # path('refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    # path('users/me/', UserMeView.as_view(), name='user_me'),
    path('guest/session/', GuestSessionView.as_view(), name='guest_session'),
    path('check/', AuthCheckView.as_view(), name='auth_check'),
]