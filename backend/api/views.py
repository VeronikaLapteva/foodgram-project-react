from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import Subscription

from .filters import IngredientSearchFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (CreateRecipeSerializer, CustomUserSerializer,
                          FavoriteSerializer, IngredientSerializer,
                          RecipeReadSerializer, ShoppingCartSerializer,
                          SubscriptionSerializer, TagSerializer)

User = get_user_model()


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (AllowAny,)

    def subscribed(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        serializer = SubscriptionSerializer(
            author, context={'request': request})
        serializer.validate(serializer.data)
        Subscription.objects.get_or_create(user=request.user, author=author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def unsubscribed(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        request.user.follower.filter(author=author).delete()
        return Response({"message": "Вы отписались от автора рецепта!"},
                        status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, pk):
        if request.method == "DELETE":
            return self.unsubscribed(request, pk)
        return self.subscribed(request, pk)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = SubscriptionSerializer(
            paginated_queryset, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)


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
    """Вьюсет для рецепта."""
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == "POST" or self.request.method == "PATCH":
            return CreateRecipeSerializer
        return RecipeReadSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if request.method == 'POST':
            serializer = FavoriteSerializer(
                recipe, context={'request': request})
            serializer.validate_favorite(serializer.data)
            Favorite.objects.create(user=user, recipe=recipe)
            return Response(data=serializer.data,
                            status=status.HTTP_201_CREATED)
        deleted = get_object_or_404(Favorite, user=user, recipe=recipe)
        deleted.delete()
        return Response({'message': 'Рецепт удален из избранного'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if request.method == 'POST':
            serializer = ShoppingCartSerializer(
                recipe, context={'request': request})
            serializer.validate_shopping_cart(serializer.data)
            ShoppingCart.objects.create(user=user, recipe=recipe)
            return Response(data=serializer.data,
                            status=status.HTTP_201_CREATED)
        deleted = get_object_or_404(ShoppingCart, user=user, recipe=recipe)
        deleted.delete()
        return Response({'message': 'Рецепт удален из списка покупок'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Отправка файла со списком покупок."""
        ingredients = IngredientRecipe.objects.filter(
            recipe__carts__user=request.user
        ).values(
            'ingredient__name', 'ingredient__units'
        ).annotate(ingredient_amount=Sum('amount'))
        shopping_cart = ['Список покупок:\n']
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__units']
            amount = ingredient['ingredient_amount']
            shopping_cart.append(f'\n{name} - {amount}, {unit}')
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = \
            'attachment; filename="shopping_cart.txt"'
        return response
