from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # 비밀번호 입력 전용

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone_number=validated_data.get('phone_number', '')
        )
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email
        }
        return data

class GuestSessionSerializer(serializers.Serializer):
    session_id = serializers.CharField(read_only=True)

    def create(self, validated_data):
        return {'session_id': validated_data.get('session_id')}

    def to_representation(self, instance):
        if isinstance(instance, dict):
            return {'session_id': instance.get('session_id')}
        return {'session_id': instance}


class AuthCheckSerializer(serializers.Serializer):
    is_authenticated = serializers.BooleanField(read_only=True)
    session_id = serializers.CharField(read_only=True, allow_null=True)
    user = UserSerializer(read_only=True, allow_null=True)