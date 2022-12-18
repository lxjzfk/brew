import csv

from collections import namedtuple

from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.template import loader
from django.views.generic import ListView

from .models import BlendIngredient, Recipe, Blend, Ingredient

# Create your views here.

def recipes(request):
    recipes = Recipe.objects.all()
    for recipe in recipes:
        if recipe.blend is not None:
            recipe.ingredients = recipe.blend.ingredients.select_related()
            for ingredient in recipe.ingredients:
                ingredient.amount = BlendIngredient.objects.get(blend=recipe.blend, ingredient=ingredient).amount
                ingredient.unit = BlendIngredient.objects.get(blend=recipe.blend, ingredient=ingredient).unit
                ingredient.ratio = "{0:.0%}".format(BlendIngredient.objects.get(blend=recipe.blend, ingredient=ingredient).get_ingredient_ratio())
    template = loader.get_template('brew/recipes.html')
    context = {
        'recipes': recipes
    }
    return HttpResponse(template.render(context, request))

def recipe_detail(request, recipe_id):
    """Display recipe details"""

    try:
        recipe = Recipe.objects.get(pk=recipe_id)
        if recipe.blend is not None:
            recipe.ingredients = recipe.blend.ingredients.select_related()
            for ingredient in recipe.ingredients:
                ingredient.amount = BlendIngredient.objects.get(blend=recipe.blend, ingredient=ingredient).amount
                ingredient.unit = BlendIngredient.objects.get(blend=recipe.blend, ingredient=ingredient).unit
                ingredient.ratio = "{0:.0%}".format(BlendIngredient.objects.get(blend=recipe.blend, ingredient=ingredient).get_ingredient_ratio())

    except Recipe.DoesNotExist:
        raise Http404("recipe doesn't exist")
    return render(request, 'brew/recipe_detail.html', {'recipe': recipe})

def check_recipe(request, recipe_id):
    """Check recipe from file prior to loading"""
    Entry = namedtuple('Entry', 'blend_name blend_ingredient_name blend_ingredient_amount blend_ingredient_unit blend_ingredient_cost total_cost weight_ratio notes')
    note = ""
    data = []
    blends = []
    blend_ingredients = []
    blend_dir = ''
    ingredient_id = 0

    try:
        recipe = Recipe.objects.get(pk=recipe_id)
        if recipe.blend is None:
            with open(recipe.file.path) as recipe_file_path:
                for entry in list(csv.DictReader(recipe_file_path)):
                    data.append(
                        Entry(
                            entry['Blend.name'], entry['BlendIngredient.name'], entry['BlendIngredient.amount'], entry['BlendIngredient.unit'], entry['BlendIngredient.cost'], "%.4f".format(round(float(entry['total cost']))), entry['weight ratio'], entry['Notes']
                        )
                    )
            
            for entry in data:
                blend = Blend.objects.get_or_create(name=entry.blend_name)
                blend_id = blend[0].pk
                blend_dir = blend[0].pk
                ingredient = Ingredient.objects.get_or_create(name=entry.blend_ingredient_name)
                ingredient_id = ingredient[0].pk
                blend_ingredient = BlendIngredient.objects.get_or_create(ingredient=ingredient[0], blend=blend[0], amount=entry.blend_ingredient_amount, unit=entry.blend_ingredient_unit, cost=entry.blend_ingredient_cost)

                blends.append(blend[0])
                
                for item in blend[0].ingredients.select_related():
                    item.amount = BlendIngredient.objects.get(blend=blend[0], ingredient=item, amount=entry.blend_ingredient_amount).amount
                    item.unit = BlendIngredient.objects.get(blend=blend[0], ingredient=item, amount=entry.blend_ingredient_amount).unit
                    item.ratio = "{0:.0%}".format(BlendIngredient.objects.get(blend=blend[0], ingredient=item, amount=entry.blend_ingredient_amount).get_ingredient_ratio())
                    blend_ingredients.append(item)

        if recipe.blend is not None:
            note = "Recipe blend is currently present"

    except Recipe.DoesNotExist:
        raise Http404("recipe doesn't exist")
    return render(request, 'brew/check_recipe.html', {'recipe': recipe, 'note': note, 'data': data, 'blends': blends, 'blend_ingredients': blend_ingredients})

def load_recipe(request, recipe_id):
    """Load recipe from file"""
    Entry = namedtuple('Entry', 'blend_name blend_ingredient_name blend_ingredient_amount blend_ingredient_unit blend_ingredient_cost total_cost weight_ratio notes')
    note = ""
    data = []

    try:
        recipe = Recipe.objects.get(pk=recipe_id)
        if recipe.blend is None:
            with open(recipe.file.path) as recipe_file_path:
                for entry in list(csv.DictReader(recipe_file_path)):
                    data.append(
                        Entry(
                            entry['Blend.name'],
                            entry['BlendIngredient.name'],
                            entry['BlendIngredient.amount'],
                            entry['BlendIngredient.unit'],
                            entry['BlendIngredient.cost'],
                            entry['total cost'],
                            entry['weight ratio'],
                            entry['Notes']
                        )
                    )
                
        if recipe.blend is not None:
            note = "Recipe blend is currently present"

    except Recipe.DoesNotExist:
        raise Http404("recipe doesn't exist")
    return render(request, 'brew/load_recipe.html', {'recipe': recipe, 'note': note, 'data': data})
