from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingList, Tag)

admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Favorite)
admin.site.register(ShoppingList)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline, )

    def validate(self, data):
        if not data.get('recipe_ingredients'):
            raise ValidationError(
                'Нужно добавить в рецепт хотя бы один ингредиент!')
        for ingredient in data.get('recipe_ingredients'):
            if ingredient.get('amount') < 0:
                raise ValidationError(
                    'Количество ингредиентов должно быть не меньше одного!')
        if not data.get('tags'):
            raise ValidationError(
                'Нужно выбрать хотя бы один тег!')
        return data
