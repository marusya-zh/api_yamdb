from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )


class SignUpSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=(UniqueValidator(queryset=User.objects.all()),)
    )
    email = serializers.EmailField(
        max_length=254,
        validators=(UniqueValidator(queryset=User.objects.all()),)
    )

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate_username(self, value):
        if value.lower() == settings.USER_ME:
            raise serializers.ValidationError(
                'Для имени нельзя использовать {value}'
            )
        return value


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    confirmation_code = serializers.CharField(max_length=100)

    class Meta:
        model = User
        fields = (
            'username',
            'confirmation_code'
        )
