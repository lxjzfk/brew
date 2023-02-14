import datetime
import csv
from django.db import models


class Ingredient(models.Model):
    name = models.CharField(max_length=40, unique=True)

    def __str__(self) -> str:
        return self.name


class Brew(models.Model):
    name = models.CharField(max_length=80)
    created = models.DateTimeField(auto_now=False, auto_now_add=True, blank=True)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='BrewIngredient',
        blank=True
    )

    def __str__(self) -> str:
        return self.created.strftime("%Y-%m-%d %H:%M:%S") + " " + self.name

    def add_ingredient(self, ingredient, amount):
        BrewIngredient.objects.create(
            ingredient=ingredient,
            brew=self,
            amount=amount
        )
    
    def get_ingredient_amount(self, ingredient):
        return BrewIngredient.objects.get(ingredient=ingredient, brew=self).amount

    def get_total_ingredient_amounts(self):
        return sum(list(map(lambda i: i.amount, BrewIngredient.objects.filter(brew=self))))

    def get_ingredient_ratio(self, ingredient):
        return self.get_ingredient_amount(ingredient) / self.get_total_ingredient_amounts()

    def get_ingredients_ratio(self, ingredient1, ingredient2):
        ingredient1_amount = self.get_ingredient_amount(ingredient1)
        ingredient2_amount = self.get_ingredient_amount(ingredient2)
        return ingredient1_amount / (ingredient1_amount + ingredient2_amount)

class BrewIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    brew = models.ForeignKey(Brew, on_delete=models.CASCADE)
    amount = models.IntegerField()

    def __str__(self) -> str:
        return self.brew.__str__() + " " + self.ingredient.name

class Blend(models.Model):
    name = models.CharField(max_length=80)
    created = models.DateTimeField(auto_now=False, auto_now_add=True, blank=True)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='BlendIngredient',
        blank=True
    )

    def __str__(self) -> str:
        return self.created.strftime("%Y-%m-%d %H:%M:%S") + " " + self.name

    def add_ingredient(self, ingredient, amount, cost=1):
        BlendIngredient.objects.create(
            ingredient=ingredient,
            blend=self,
            amount=amount,
            cost=cost
        )

    def add_blend(self, blend, amount):
        for ingredient in blend.ingredients.all():
            ingredient_amount = blend.get_ingredient_ratio(ingredient) * amount
            self.add_ingredient(ingredient, ingredient_amount)
    
    def get_ingredient_amount(self, ingredient):
        return sum(blend_ingredient.amount for blend_ingredient in BlendIngredient.objects.filter(ingredient=ingredient, blend=self))

    def get_total_ingredient_amounts(self):
        return sum(list(map(lambda i: i.amount, BlendIngredient.objects.filter(blend=self))))

    def get_ingredient_ratio(self, ingredient):
        return self.get_ingredient_amount(ingredient) / self.get_total_ingredient_amounts()

    def get_ingredients_ratio(self, ingredient1, ingredient2):
        ingredient1_amount = self.get_ingredient_amount(ingredient1)
        ingredient2_amount = self.get_ingredient_amount(ingredient2)
        return ingredient1_amount / (ingredient1_amount + ingredient2_amount)


class BlendIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    blend = models.ForeignKey(Blend, on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=5, max_digits=12)
    unit = models.CharField(max_length=5)
    cost = models.DecimalField(max_digits=10, decimal_places=4)

    class Meta:
        unique_together = ('ingredient', 'blend', 'amount', 'unit', 'cost')

    def __str__(self) -> str:
        return self.blend.__str__() + " " + self.ingredient.name

    def get_ingredient_ratio(self):
        return self.blend.get_ingredient_ratio(self.ingredient)


class Recipe(models.Model):
    name = models.CharField(max_length=40)
    file = models.FileField(verbose_name='Recipe File', blank=True)
    created = models.DateTimeField(auto_now=False, auto_now_add=True, null=True, blank=True)
    modified = models.DateTimeField(auto_now_add=True, null=True)
    blend = models.ManyToManyField(
        Blend,
        through='RecipeBlend',
        blank=True
    )

    def __str__(self) -> str:
        return self.created.strftime("%Y-%m-%d %H:%M:%S") + " " + self.name
    
    def add_blend(self, blend):
        new_blend = RecipeBlend.objects.get_or_create(
            blend=blend,
            recipe=self
        )
        
        if(new_blend[1]):
            return "What do I do with this?"
        else:
            return "Already exists."


    def export_recipe_to_csv(self):
        status = "Exporting to CSV"
        headers = ['blend', 'ingredient', 'amount', 'unit', 'cost', 'total', 'ratio']

        with open(self.name + '.csv', 'w', newline='') as csvfile:
            status = "Writing to CSV"
            recipe_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            blends = self.blend.select_related()
            if(blends):
                for blend in blends:
                    for blend_ingredient in BlendIngredient.objects.filter(blend=blend):
                        recipe_writer.writerow([blend_ingredient.blend.name, blend_ingredient.ingredient.name, blend_ingredient.amount, blend_ingredient.unit, blend_ingredient.cost, blend_ingredient.amount * blend_ingredient.cost, blend_ingredient.get_ingredient_ratio()])
        
        self.file = self.name + '.csv'
        status = 'CSV Writing Success'
        return status

    def import_recipe_from_csv(self):
        status = "Importing from CSV"
        headers = ['blend', 'ingredient', 'amount', 'unit', 'cost', 'total', 'ratio']
        blend_for_import = None

        with open(self.name + '.csv', 'w', newline='') as csvfile:
            status = "Reading from CSV"
            blend_reader = csv.reader(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            
            for blend_ingredient in blend_reader:
                ingredient = blend_reader.readrow()
                try:
                    BlendIngredient.objects.get_or_create(name=ingredient.name)
                except:
                    raise ImportError
                
                try:
                    blend_for_import.add_ingredient(ingredient)
                except:
                    raise RuntimeError
                else:
                    pass
        
        self.file = csvfile
        status = 'Import Success'
        return status


class RecipeBlend(models.Model):
    added = models.DateTimeField(auto_now=False, auto_now_add=True, null=True, blank=True)
    blend = models.ForeignKey(Blend, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
