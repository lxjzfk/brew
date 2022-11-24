import datetime

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
        return BlendIngredient.objects.get(ingredient=ingredient, blend=self).amount

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
    blend = models.ForeignKey(Blend, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self) -> str:
        return self.created.strftime("%Y-%m-%d %H:%M:%S") + " " + self.name
