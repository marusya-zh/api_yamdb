from datetime import datetime as dt

from django.contrib.auth import get_user_model

from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title

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


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')

    def get_rating(self, obj):
        return obj.rating


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')

    def validate_year(self, value):
        if value > dt.now().year:
            raise serializers.ValidationError("Недопустимое значение поля. "
                                              "Год больше текущего.")
        return value

    def get_rating(self, obj):
        return obj.rating

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['genre'] = GenreSerializer(instance.genre.all(), many=True).data
        rep['category'] = CategorySerializer(instance.category).data
        return rep


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('title',)
        extra_kwargs = {'score': {'required': True}}

    def validate_score(self, value):
        if not 0 < value <= 10:
            raise serializers.ValidationError(
                "Недопустимое значение поля. Оценка вне диапазона от 1 до 10."
            )
        return value

    def create(self, validated_data):
        author = validated_data.get('author')
        title = validated_data.get('title')

        if Review.objects.filter(author=author, title=title).exists():
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        "The fields title, author must make a unique set."
                    ]
                }
            )

        return Review.objects.create(**validated_data)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('review',)
