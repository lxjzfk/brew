import csv
from datetime import datetime
from decimal import Decimal
from collections import namedtuple

from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.template import loader
from django.views.generic import ListView

from .models import BlendIngredient, Recipe, Blend, Ingredient

class RecipesListView(ListView):
    template_name = 'brew/recipies_list.html'
    model = Recipe
    context_object_name = 'recipies'

def recipes(request):
    recipes = Recipe.objects.all()

    for recipe in recipes:
        recipe_blends = recipe.blend.select_related()
        if recipe_blends is not None:
            for blend in recipe_blends:
                blend_ingredients = blend.ingredients.select_related()
                for ingredient in blend_ingredients:
                    ingredient.amount = BlendIngredient.objects.get(
                        blend=recipe.blend, ingredient=ingredient).amount
                    ingredient.unit = BlendIngredient.objects.get(
                        blend=recipe.blend, ingredient=ingredient).unit
                    ingredient.ratio = "{0:.0%}".format(BlendIngredient.objects.get(
                        blend=recipe.blend, ingredient=ingredient).get_ingredient_ratio())
    
    template = loader.get_template('brew/recipes.html')
    context = {
        'recipes': recipes
    }
    return HttpResponse(template.render(context, request))

def recipe_detail(request, recipe_id):
    """Display recipe details"""

    try:
        recipe = Recipe.objects.get(pk=recipe_id)
        recipe_blends = recipe.blend.select_related()
        if recipe_blends is not None:
            for blend in recipe_blends:
                blend_ingredients = blend.ingredients.select_related()
                for ingredient in blend_ingredients:
                    ingredient.amount = BlendIngredient.objects.get(blend=recipe.blend, ingredient=ingredient).amount
                    ingredient.unit = BlendIngredient.objects.get(blend=recipe.blend, ingredient=ingredient).unit
                    ingredient.ratio = "{0:.0%}".format(BlendIngredient.objects.get(blend=recipe.blend, ingredient=ingredient).get_ingredient_ratio())

    except Recipe.DoesNotExist:
        raise Http404("recipe doesn't exist")
    return render(request, 'brew/recipe_detail.html', {'recipe': recipe})

def check_recipe_file(request, recipe_id):
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
        recipe_blends = recipe.blend.select_related()
        if recipe_blends.count() == 0:
            with open(recipe.file.path) as recipe_file_path:
                for entry in list(csv.DictReader(recipe_file_path)):
                    cost_per_unit = entry['cost/unit']
                    try:
                        # Best to store the values in scientific notation
                        cost_per_unit = float(cost_per_unit)
                    except ValueError:
                        # Can't convert string to float
                        cost_per_unit = Decimal(cost_per_unit.strip('$'))
                    
                    total_cost = entry['total cost']
                    try:
                        # Best to store the values in scientific notation
                        total_cost = float(total_cost)
                    except ValueError:
                        # Can't convert string to float
                        total_cost = Decimal(total_cost.strip('$'))

                    data.append(
                        Entry(
                            entry['Name'], entry['item'], entry['amount'], entry['unit'], cost_per_unit, total_cost, entry['weight ratio'], entry['Notes']
                        )
                    )
            
            for entry in data:
                # UP TO HERE
                # Shouldn't be creating anything at this stage
                # Should be coming up with a list of things that need to be done
                # i.e. Need to create X number of blend entries (enumerate)
                #       and X number of ingredients (enumerate)
                # Also would be good to facilitate aliases or matching for ingredients
                # If possible, would possibly be able to get average statistics for
                # ingredient items. Also, could describe attributes, such as
                # "cut", "organic", "fine", "leaf", "aged", "roasted", etc.

                try:
                    blend = Blend.objects.get(name=entry.blend_name)
                except:
                    blend = Blend(name=entry.blend_name, created=datetime.now())
                
                #ingredient = Ingredient.objects.get(name=entry.blend_ingredient_name)
                #blend_ingredient = BlendIngredient.objects.get(ingredient=ingredient[0], blend=blend[0], amount=entry.blend_ingredient_amount, unit=entry.blend_ingredient_unit, cost=entry.blend_ingredient_cost)

                blends.append(blend)
                
                for item in blend.ingredients.select_related():
                    try:
                        blend_ingredient = BlendIngredient.objects.get(blend=blend, ingredient=item, amount=entry.blend_ingredient_amount)
                    except:
                        item.blend_ingredient_amount = entry.blend_ingredient_amount
                        item.blend_ingredient_unit = entry.blend_ingredient_unit
                        item.weight_ratio = entry.weight_ratio
                    else:
                        item.amount = blend_ingredient.amount
                        item.blend_ingredient_unit = blend_ingredient.unit
                        item.weight_ratio = "{0:.0%}".format(blend_ingredient.get_ingredient_ratio())
                    blend_ingredients.append(item)
        else:
            note = "Recipe currently has {} present.".format(recipe_blends)

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
