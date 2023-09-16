# from django.core.files.base import ContentFile
from recipes.models import Ingredient, Recipe, Tag, IngredientRecipe
from rest_framework import serializers
# from rest_framework.relations import SlugRelatedField
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model
from rest_framework.fields import SerializerMethodField
from users.models import Subscription
from drf_extra_fields.fields import Base64ImageField

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор создания пользователя"""

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'id',
            'username',
            'email',
            'password',
            'first_name',
            'last_name'
        )


class CustomUserSerializer(UserSerializer):
    """Сериализатор профиля пользователя"""
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name'
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class ReadIngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения ингредиентов в рецепте"""
    id = serializers.ReadOnlyField(
        source='ingredient.id',
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name',
    )
    units = serializers.ReadOnlyField(
        source='ingredient.units',
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'units', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецепта"""
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    image = Base64ImageField()
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'description',
            'cooking_time',
        )

    def get_ingredients(self, obj):
        ingredients = obj.recipe_ingredients.all()
        return ReadIngredientRecipeSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.shopping_cart.filter(recipe=obj).exists()


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'user', 'author')
