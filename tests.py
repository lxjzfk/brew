from django.test import TestCase
from brew.models import Brew, Ingredient, BrewIngredients

class BrewTestCase(TestCase):
    def setUp(self):
        Brew.objects.create(name="Brew")
        Ingredient.objects.create(name="Dandelion Root")
        self.brew = Brew.objects.get(name="Brew")
        self.ingredient = Ingredient.objects.get(name="Dandelion Root")
        self.brew.add_ingredient(self.ingredient, 1)
        
    def test_brew_has_name(self):
        brew = Brew.objects.get(name="Brew")
        self.assertEqual(brew.name, "Brew")
    
    def test_ingredient_has_name(self):
        ingredient = Ingredient.objects.get(name="Dandelion Root")
        self.assertEqual(ingredient.name, "Dandelion Root")

    def test_brew_can_have_ingredients(self):
        self.assertGreater(self.brew.ingredients.count(), 0)
        
    def test_brew_ingredients_have_amounts(self):
        self.assertIsInstance(self.brew.ingredients.first().brewingredients_set.first().amount, int)
