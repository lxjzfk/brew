from django.test import TestCase
import os.path
from brew.models import Blend, Brew, Ingredient, Recipe


class SimpleBrewTestCase(TestCase):
    fixtures = ['brew.yaml']

    def setUp(self):
        self.brew = Brew.objects.get(name="Simple Brew")
        self.dandelion = Ingredient.objects.get(name="Dandelion Root")
        self.tulsi = Ingredient.objects.get(name="Tulsi")
        
    def test_brew_has_name(self):
        brew = Brew.objects.all().first()
        self.assertIs(type(brew.name), str)
    
    def test_ingredient_has_name(self):
        ingredient = Ingredient.objects.get(name="Dandelion Root")
        self.assertEqual(ingredient.name, "Dandelion Root")

    def test_brew_can_have_ingredients(self):
        self.assertGreater(self.brew.ingredients.count(), 0)
        
    def test_brew_ingredients_have_amounts(self):
        self.assertIsInstance(self.brew.ingredients.first().brewingredient_set.first().amount, int)

    def test_brew_has_two_ingredients(self):
        self.assertEquals(self.brew.ingredients.count(), 2)

    def test_can_determine_brew_ingredient_ratios(self):
        self.assertEquals(self.brew.get_ingredient_ratio(self.dandelion), 0.5)
        self.assertEquals(self.brew.get_ingredients_ratio(self.dandelion, self.tulsi), 0.5)


class ComplexBrewTestCase(TestCase):
    fixtures = ['brew.yaml']

    def setUp(self):
        self.brew = Brew.objects.get(name="Complex Brew")
        self.dandelion = Ingredient.objects.get(name="Dandelion Root")
        self.tulsi = Ingredient.objects.get(name="Tulsi")
        self.licorice = Ingredient.objects.get(name="Licorice")
        self.brew.add_ingredient(self.dandelion, 1)
        self.brew.add_ingredient(self.tulsi, 1)
        self.brew.add_ingredient(self.licorice, 1)
        
    def test_brew_has_three_ingredients(self):
        self.assertEquals(self.brew.ingredients.count(), 3)

    def test_can_determine_brew_ingredient_ratios(self):
        self.assertEquals(self.brew.get_ingredient_ratio(self.dandelion), 1/3)
        self.assertEquals(self.brew.get_ingredients_ratio(self.dandelion, self.tulsi), 0.5)

class SimpleBlendTestCase(TestCase):
    fixtures = ['brew.yaml']

    def setUp(self):
        self.blend = Blend.objects.get(name="Simple Blend")
    
    def test_blend_has_one_ingredients(self):
        self.assertEquals(self.blend.ingredients.count(), 1)

class CombinationBlendTestCase(TestCase):
    fixtures = ['brew.yaml']

    def setUp(self):
        self.blend1 = Blend.objects.create(name="First Blend")
        self.blend2 = Blend.objects.create(name="Second Blend")
        self.combination_blend = Blend.objects.get(name="Combination Blend")
        self.dandelion = Ingredient.objects.get(name="Dandelion Root")
        self.tulsi = Ingredient.objects.get(name="Tulsi")
        self.licorice = Ingredient.objects.get(name="Licorice")
        self.ginger = Ingredient.objects.get(name="Ginger Root")
        self.assam = Ingredient.objects.get(name="Black Assam Tea")
        self.cinnamon = Ingredient.objects.get(name="Cinnamon")
        self.blend1.add_ingredient(self.dandelion, 1)
        self.blend1.add_ingredient(self.tulsi, 1)
        self.blend1.add_ingredient(self.licorice, 1)
        self.blend2.add_ingredient(self.ginger, 1)
        self.blend2.add_ingredient(self.assam, 1)
        self.blend2.add_ingredient(self.cinnamon, 1)
        self.combination_blend.add_blend(self.blend1, 3)
        self.combination_blend.add_blend(self.blend2, 3)
        
    def test_combination_blend_has_six_ingredients(self):
        self.assertEquals(self.combination_blend.ingredients.count(), 6)

class RecipeTestCase(TestCase):
    fixtures = ['brew.yaml']

    def setUp(self):
        self.recipe = Recipe.objects.get(name="Test Recipe")
        self.blend = Blend.objects.get(name="Simple Blend")
        self.dandelion = Ingredient.objects.get(name="Dandelion Root")
        self.tulsi = Ingredient.objects.get(name="Tulsi")
        self.licorice = Ingredient.objects.get(name="Licorice")
        self.blend.add_ingredient(self.dandelion, 1)
        self.blend.add_ingredient(self.tulsi, 1)
        self.blend.add_ingredient(self.licorice, 1)
        self.recipe = Recipe.objects.get_or_create(name="Test")[0]
        self.recipe.add_blend(self.blend)

    def test_can_export_recipe_to_csv(self):
        self.recipe.export_recipe_to_csv()
        self.assertTrue(os.path.exists(self.recipe.file.path))
    
    def can_import_recipe_from_csv(self):
        status = self.recipe.import_recipe_from_csv()
        self.assertEquals(status, 'Import Success')