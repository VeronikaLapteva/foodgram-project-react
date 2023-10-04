from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient, RecipeTag,
                     ShoppingList, Tag)

admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Favorite)
admin.site.register(ShoppingList)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0
    min_num = 1


class RecipeTagtInline(admin.TabularInline):
    model = RecipeTag
    extra = 0
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline, RecipeTagtInline,)
