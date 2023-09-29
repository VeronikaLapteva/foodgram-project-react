from django.contrib import admin

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
