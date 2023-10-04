from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingList, Tag)
from rest_framework import serializers, status
from rest_framework.validators import ValidationError
from users.models import Subscription

User = get_user_model()


class UserMeSerializer(UserSerializer):
    """Сериализатор профиля пользователя."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        if (self.context.get('request')
           and not self.context['request'].user.is_anonymous):

            return Subscription.objects.filter(
                user=self.context['request'].user, author=obj).exists()

        return False


class RegistrationSerializer(UserCreateSerializer):
    """Сериализатор регистрации пользователя."""
    email = serializers.EmailField(max_length=228,
                                   validators=[validate_email]
                                   )
    username = serializers.CharField(max_length=228)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = "__all__"


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов в рецепте."""
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient.id', queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов."""
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredients', read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    author = UserMeSerializer(read_only=True)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time', ]

    def get_is_in_shopping_cart(self, obj):
        current_user = self.context.get('request').user
        return (not current_user.is_anonymous
                and ShoppingList.objects.filter(
                    recipe=obj, user=current_user).exists()
                )

    def get_is_favorited(self, obj):
        current_user = self.context.get('request').user
        return (not current_user.is_anonymous
                and Favorite.objects.filter(
                    recipe=obj, user=current_user).exists()
                )


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецептов."""
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients', many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    image = Base64ImageField(allow_null=True, required=False)
    author = UserMeSerializer(read_only=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'ingredients', 'tags', 'image', 'name',
                  'text', 'author', 'cooking_time', ]

    def create(self, validated_data):
        author = self.context.get('request').user
        ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data, author=author)
        recipe.tags.set(tags)
        ingredients_list = []
        for ingredient_data in ingredients:
            ingredient_id = ingredient_data['ingredient']['id']
            current_amount = ingredient_data.get('amount')
            ingredients_list.append(
                RecipeIngredient(recipe=recipe, ingredient=ingredient_id,
                                 amount=current_amount))
        RecipeIngredient.objects.bulk_create(ingredients_list)
        return recipe

    def validate(self, data):
        if not data.get('recipe_ingredients'):
            raise serializers.ValidationError(
                'Нужно добавить в рецепт хотя бы один ингредиент!')
        for ingredient in data.get('recipe_ingredients'):
            if ingredient.get('amount') < 0:
                raise serializers.ValidationError(
                    'Количество ингредиентов должно быть не меньше одного!')
        if not data.get('tags'):
            raise serializers.ValidationError(
                'Нужно выбрать хотя бы один тег!')
        return data

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.add(*tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        ingredients_list = []
        for ingredient_data in ingredients:
            ingredient_id = ingredient_data['ingredient']['id']
            current_amount = ingredient_data.get('amount')
            ingredients_list.append(
                RecipeIngredient(recipe=instance, ingredient=ingredient_id,
                                 amount=current_amount))
        RecipeIngredient.objects.bulk_create(ingredients_list)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(
            instance, context={'request': self.context.get('request')}).data


class UserRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для подписчиков."""
    image = Base64ImageField(read_only=True)
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time', ]
        read_only_fields = ('__all__',)


class AuthorSubscriptionsSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = UserRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        current_user = self.context.get('request').user
        return (
            current_user.follower.filter(author=obj).exists()
            if not current_user.is_anonymous
            else False
        )

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Subscription.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail='Вы не можете подписаться на самого себя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data
