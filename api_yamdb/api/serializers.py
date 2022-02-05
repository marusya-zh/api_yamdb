from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(max_length=254)

    def validate(self, data):
        if data['username'] == 'me':
            raise serializers.ValidationError(
                'Использовать имя \'me\' в качестве username запрещено.'
            )

        email = data.get('email')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                f'Пользователь с email \'{email}\' уже существует.'
            )

        username = data.get('username')
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                f'Пользователь \'{username}\' уже существует.'
            )

        return data


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField(max_length=20)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
