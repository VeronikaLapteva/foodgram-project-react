from django.contrib import admin

from recipes.models import (Ingredient, Tag, Recipe,
                            IngredientRecipe, Favorite, ShoppingCart)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'units')
    search_fields = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'author', 'count_favorites')
    list_filter = ('author', 'name', 'tags',)

    def count_favorites(self, obj):
        return obj.favorites.count()


class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientRecipe, IngredientRecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
