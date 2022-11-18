from django.contrib import admin
from .models import Ingredient, Brew, Blend, BlendIngredient

admin.site.register(Ingredient)
admin.site.register(Brew)
admin.site.register(Blend)
admin.site.register(BlendIngredient)
