from django.contrib.auth import get_user_model
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=64, verbose_name='Название ингредиета')
    units = models.CharField(max_length=64, verbose_name='Единица измерения')

    def __str__(self):
        return f'{self.name}, {self.units}'


class Tag(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название тега')
    color = models.CharField(
        unique=True,
        max_length=7,
        verbose_name='Цвет тега'
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Slug',
        validators=[
            RegexValidator(
                regex=r"^[-a-zA-Z0-9_]+$",
                message="Slug должен содержать только буквы, цифры, "
                "дефисы и знаки подчеркивания.",
            ),
        ],
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=200, verbose_name='Теги')
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты')
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1, message='Минимальное значение 1!')],
        verbose_name='Время приготовления')
    description = models.TextField(max_length=256, verbose_name='Описание')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')
    author = models.ForeignKey(
        User,
        related_name='recipe',
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Автор'
    )
    image = models.ImageField(
        upload_to='recipe/',
        null=True,
        default=None,
        verbose_name='Изображение'
    )

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients_recipe')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_recipe')
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1, message='Минимальное количество 1!'),
                    MaxValueValidator(2000,
                                      message='Максимальное количество!')],
        verbose_name='Количество'
    )

    def __str__(self):
        return (f'{self.ingredient.name} {self.ingredient.units}'
                f' - {self.amount} ')


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'recipe'],
                             name='unique_favourite')
        ]

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Избранное'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='shopping_cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт',)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'recipe'],
                             name='unique_shopping_cart')
        ]

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Корзину покупок'
