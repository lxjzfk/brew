from django.test import TestCase
from brew.models import Brew, Ingredient

class BrewTestCase(TestCase):
    def setUp(self):
        Brew.objects.create(name="Brew")
        Ingredient.objects.create(name="Dandelion Root")
        brew = Brew.objects.get(name="Brew")
        ingredient = Ingredient.objects.get(name="Dandelion Root")
        brew.add_ingredient(ingredient)
    
    def test_brew_has_name(self):
        brew = Brew.objects.get(name="Brew")
        self.assertEqual(brew.name, "Brew")
    
    def test_ingredient_has_name(self):
        ingredient = Ingredient.objects.get(name="Dandelion Root")
        self.assertEqual(ingredient.name, "Dandelion Root")

    def test_brew_can_have_ingredients(self):
        pass
        

