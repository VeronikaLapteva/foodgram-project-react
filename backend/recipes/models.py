from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=50,
        blank=False,
        verbose_name="Название тега",
        unique=True,
    )
    color = models.CharField(
        max_length=10,
        blank=False,
        verbose_name="Цвет тега",
        unique=True,
    )
    slug = models.SlugField(
        max_length=50,
        blank=False,
        verbose_name="slug",
        unique=True,
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=50,
        blank=False,
        verbose_name="Название ингредиента",
        unique=False,
    )
    measurement_unit = models.CharField(
        max_length=200,
        blank=False,
        verbose_name="Единицы измерения",
        unique=False,
    )

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        verbose_name="Автор рецепта",
        related_name="recipes",
    )
    name = models.CharField(
        max_length=90,
        blank=False,
        verbose_name="Название рецепта",
        unique=False,
    )
    image = models.ImageField(
        upload_to="images",
        blank=False,
        verbose_name="Изображение рецепта",
        null=True,
    )
    text = models.TextField(
        max_length=2500,
        blank=False,
        verbose_name="Описание рецепта",
        unique=True,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        through_fields=("recipe", "ingredient",),
    )
    tags = models.ManyToManyField(
        Tag,
        through="RecipeTag",
        related_name="recipes"
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления",
        validators=[
            MinValueValidator(1, message="Время приготовления "
                              "должно быть не менее 1 минуты."),
        ]
    )
    created = models.DateTimeField(
        verbose_name="Дата добавления",
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created"]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, message="Количество ингредиентов должно быть"
                              "не менее 1!"),
        ]
    )


class RecipeTag(models.Model):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        blank=False,
        verbose_name="Тег в рецепте",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        blank=False,
        verbose_name="Рецепт с тегами",
    )


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        blank=False,
        verbose_name="Рецепт",
        related_name="favorite_recipe",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        verbose_name="Пользователь",
        related_name="favorite_user",
    )

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Избранное'


class ShoppingList(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        blank=False,
        verbose_name="Рецепт в покупках",
        related_name="shopping_list_recipe",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        verbose_name="Пользователь",
        related_name="shopping_list_user",
    )

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Корзину покупок'
