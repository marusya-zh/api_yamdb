from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404

from django_filters import rest_framework as dfrf_filters

from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Review, Title
from .pagination import UserPagination
from .permissions import (IsAdminPermission, IsModeratorPermission,
                          IsOwnerPermission, ReadOnlyPermission)
from .serializers import (SignupSerializer, TokenSerializer, UserSerializer,
                          CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleReadSerializer, TitleWriteSerializer)

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = SignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.data['username']
    email = serializer.data['email']
    user, _ = User.objects.get_or_create(email=email, username=username)
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        '',
        confirmation_code,
        settings.EMAIL_ADMIN,
        [email],
        fail_silently=False
    )
    response = {
        'email': email,
        'username': username
    }
    return Response(response, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.data['username']
    confirmation_code = serializer.data['confirmation_code']
    user = get_object_or_404(User, username=username)
    if default_token_generator.check_token(user, confirmation_code):
        access_token = RefreshToken.for_user(user)
        response = {'token': str(access_token.access_token)}
        return Response(response, status=status.HTTP_200_OK)

    response = {user.username: 'Confirmation code incorrect.'}
    return Response(response, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.get_queryset().order_by('id')
    serializer_class = UserSerializer

    http_method_names = ['get', 'post', 'patch', 'delete']

    lookup_field = 'username'

    pagination_class = UserPagination

    permission_classes = (IsAdminPermission,)

    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(methods=['GET', 'PATCH'], detail=False,
            permission_classes=[IsAuthenticated])
    def me(self, request):
        user = request.user
        data = request.data
        if request.method == 'PATCH':
            serializer = self.get_serializer(user, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(role=user.role, partial=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(user)
        return Response(serializer.data)


class ListCreateDestroyViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin,
    mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    pass


class CategoryViewSet(ListCreateDestroyViewSet):
    queryset = Category.objects.get_queryset().order_by('id')
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsAdminPermission | ReadOnlyPermission,)
    lookup_field = 'slug'


class GenreViewSet(ListCreateDestroyViewSet):
    queryset = Genre.objects.get_queryset().order_by('id')
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsAdminPermission | ReadOnlyPermission,)
    lookup_field = 'slug'


class TitleFilter(dfrf_filters.FilterSet):
    category = dfrf_filters.ModelChoiceFilter(
        field_name='category',
        to_field_name='slug',
        queryset=Category.objects.all()
    )
    genre = dfrf_filters.ModelChoiceFilter(
        field_name='genre',
        to_field_name='slug',
        queryset=Genre.objects.all()
    )

    class Meta:
        model = Title
        fields = ('category', 'genre', 'year')


class TitleViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminPermission | ReadOnlyPermission,)
    filter_backends = (dfrf_filters.DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_queryset(self):
        qs = Title.objects.get_queryset().order_by('id').annotate(
            _rating=Avg('reviews__score')
        )
        name = self.request.query_params.get('name')
        if name:
            qs = qs.filter(name__contains=name)
        return qs

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsOwnerPermission | IsAdminPermission
                          | IsModeratorPermission | ReadOnlyPermission,)

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.get_queryset().order_by('id')

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsOwnerPermission | IsAdminPermission
                          | IsModeratorPermission | ReadOnlyPermission,)

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        return review.comments.get_queryset().order_by('id')

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)
