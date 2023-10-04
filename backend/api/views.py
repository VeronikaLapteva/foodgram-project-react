from django.contrib.auth import get_user_model
from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingList, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import Subscription

from .filters import RecipeFilter
from .pagination import FoodgramPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeSerializer, RegistrationSerializer,
                          SubscriptionsSerializer, TagSerializer,
                          UserMeSerializer, UserRecipeSerializer)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Вьюсет для пользователей."""
    queryset = User.objects.all()
    pagination_class = FoodgramPagination
    http_method_names = ['get', 'post', 'delete']

    def get_permissions(self):
        if self.action == 'retrieve':
            self.permission_classes = [IsAuthenticated, ]
        return super(self.__class__, self).get_permissions()

    def get_serializer_class(self):
        if self.action in ['subscriptions', 'subscribe']:
            return SubscriptionsSerializer
        if self.request.method == 'GET':
            return UserMeSerializer
        if self.request.method == 'POST':
            return RegistrationSerializer

    @action(detail=False, methods=['get'],
            pagination_class=FoodgramPagination,
            permission_classes=(IsAuthenticated,)
            )
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        serializer = SubscriptionsSerializer(
            self.paginate_queryset(queryset), many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['id'])
        if request.method == 'POST':
            serializer = SubscriptionsSerializer(
                author, data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
        if request.method == 'DELETE':
            follow = Subscription.objects.get(user=request.user,
                                              author=author)
            follow.delete()
            return Response({'detail': 'Вы отписались'},
                            status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], pagination_class=None,
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет для тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny, )


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет для ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name']
    lookup_field = 'name__istartswith'
    pagination_class = None

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrReadOnly, ]
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    pagination_class = FoodgramPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        elif self.action in ['favorite_user', 'shopping_cart', ]:
            return UserRecipeSerializer

        return RecipeCreateSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        serializer = UserRecipeSerializer(recipe, context={"request": request})
        if request.method == 'POST':
            if Favorite.objects.filter(user=request.user,
                                       recipe=recipe).exists():
                return Response({'errors': 'Рецепт уже добавлен в избранное'},
                                status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.create(user=request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not Favorite.objects.filter(user=request.user,
                                       recipe=recipe).exists():
            return Response({'errors': 'Рецепта нет в избранном'},
                            status=status.HTTP_400_BAD_REQUEST)
        favorite = get_object_or_404(Favorite, user=request.user,
                                     recipe=recipe)
        favorite.delete()
        return Response({'detail': 'Рецепт удален из избранного'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,),
            pagination_class=None)
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if request.method == 'POST':
            serializer = UserRecipeSerializer(recipe, data=request.data,
                                              context={"request": request})
            serializer.is_valid()
            if ShoppingList.objects.filter(user=request.user,
                                           recipe=recipe).exists():
                return Response(
                    {'errors': 'Рецепт уже добавлен в список покупок'},
                    status=status.HTTP_400_BAD_REQUEST)
            ShoppingList.objects.create(user=request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not ShoppingList.objects.filter(user=request.user,
                                           recipe=recipe).exists():
            return Response(
                {'errors': 'Рецепта нет в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST)
        shopping_cart = get_object_or_404(ShoppingList, user=request.user,
                                          recipe=recipe)
        shopping_cart.delete()
        return Response(
            {'detail': 'Рецепт удален из списка покупок'},
            status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            permission_classes=[IsAuthenticated, ])
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart = RecipeIngredient.objects.filter(
            recipe__shopping_list_recipe__user=user)
        ingredients = shopping_cart.values(
            name=F('ingredient__name'),
            measurement_unit=F('ingredient__measurement_unit')).annotate(
            amount=Sum('amount'))
        file_name = 'shopping_cart.txt'
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        for ingredient in ingredients:
            response.write(
                f"{ingredient['name']} - {ingredient['amount']}"
                f" {ingredient['measurement_unit']}\n")
        return response
