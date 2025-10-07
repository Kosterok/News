import django_filters
from .models import Post, Author
from django import forms

class PostFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        field_name='title',
        lookup_expr='icontains',
        label='Заголовок содержит'
    )
    author = django_filters.ModelChoiceFilter(
        queryset=Author.objects.all(),
        label='Автор'
    )
    date_after = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='date__gte',
        label='Позже даты',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = Post
        fields = []  # оставляем пустым, так как поля описаны явно
