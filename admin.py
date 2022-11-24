from django.contrib import admin
from .models import Ingredient, Brew, BrewIngredient, Blend, BlendIngredient, Recipe

admin.site.register(Ingredient)
admin.site.register(Brew)
admin.site.register(BrewIngredient)
admin.site.register(Blend)
admin.site.register(BlendIngredient)
admin.site.register(Recipe)