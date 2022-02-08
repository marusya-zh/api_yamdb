from django_filters import rest_framework as filters
from reviews.models import Category, Genre, Title


class TitleFilter(filters.FilterSet):
    category = filters.ModelChoiceFilter(
        field_name='category',
        to_field_name='slug',
        queryset=Category.objects.all()
    )
    genre = filters.ModelChoiceFilter(
        field_name='genre',
        to_field_name='slug',
        queryset=Genre.objects.all()
    )

    class Meta:
        model = Title
        fields = ('category', 'genre', 'year')
