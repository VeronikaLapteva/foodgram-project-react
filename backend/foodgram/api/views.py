from recipes.models import Recipe, Ingredient, Tag
from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from django_filters import rest_framework as filters

from .filters import IngredientSearchFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (IngredientSerializer,
                          TagSerializer,
                          RecipeSerializer)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = [IngredientSearchFilter]


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthorOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnly]
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        queryset = Recipe.objects.all().select_related(
            'author').prefetch_related('ingredients')
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
