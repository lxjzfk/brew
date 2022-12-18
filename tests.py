from django.test import TestCase

from brew.models import Blend, Brew, Ingredient, Recipe


class SimpleBrewTestCase(TestCase):
    def setUp(self):
        Brew.objects.create(name="Simple Brew")
        Ingredient.objects.create(name="Dandelion Root")
        Ingredient.objects.create(name="Tulsi")
        self.brew = Brew.objects.get(name="Simple Brew")
        self.dandelion = Ingredient.objects.get(name="Dandelion Root")
        self.tulsi = Ingredient.objects.get(name="Tulsi")
        self.brew.add_ingredient(self.dandelion, 1)
        self.brew.add_ingredient(self.tulsi, 1)
        
    def test_brew_has_name(self):
        brew = Brew.objects.get(name="Simple Brew")
        self.assertEqual(brew.name, "Simple Brew")
    
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
    def setUp(self):
        Brew.objects.create(name="Complex Brew")
        Ingredient.objects.create(name="Dandelion Root")
        Ingredient.objects.create(name="Tulsi")
        Ingredient.objects.create(name="Licorice")
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
    def setUp(self):
        self.blend = Blend.objects.create(name="Simple Blend")
        self.dandelion = Ingredient.objects.create(name="Dandelion Root")
        self.tulsi = Ingredient.objects.create(name="Tulsi")
        self.licorice = Ingredient.objects.create(name="Licorice")
        self.blend.add_ingredient(self.dandelion, 1)
        self.blend.add_ingredient(self.tulsi, 1)
        self.blend.add_ingredient(self.licorice, 1)
    
    def test_blend_has_three_ingredients(self):
        self.assertEquals(self.blend.ingredients.count(), 3)

class CombinationBlendTestCase(TestCase):
    def setUp(self):
        self.blend1 = Blend.objects.create(name="First Blend")
        self.blend2 = Blend.objects.create(name="Second Blend")
        self.combination_blend = Blend.objects.create(name="Combination Blend")
        self.dandelion = Ingredient.objects.create(name="Dandelion Root")
        self.tulsi = Ingredient.objects.create(name="Tulsi")
        self.licorice = Ingredient.objects.create(name="Licorice")
        self.ginger = Ingredient.objects.create(name="Ginger Root")
        self.assam = Ingredient.objects.create(name="Black Assam Tea")
        self.cinnamon = Ingredient.objects.create(name="Cinnamon")
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

class CSVTestCase(TestCase):
    def setUp(self):
        self.blend = Blend.objects.create(name="Simple Blend")
        self.dandelion = Ingredient.objects.create(name="Dandelion Root")
        self.tulsi = Ingredient.objects.create(name="Tulsi")
        self.licorice = Ingredient.objects.create(name="Licorice")
        self.blend.add_ingredient(self.dandelion, 1)
        self.blend.add_ingredient(self.tulsi, 1)
        self.blend.add_ingredient(self.licorice, 1)
        self.recipe = Recipe(name="Test")

    def test_can_output_csv(self):
        export = self.blend.export_to_csv()
        self.assertIs(type(export), type(self.recipe))