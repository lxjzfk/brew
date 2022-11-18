import datetime

from django.db import models


class Ingredient(models.Model):
    name = models.CharField(max_length=40)

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

    def add_ingredient(self, ingredient, amount):
        BlendIngredient.objects.create(
            ingredient=ingredient,
            blend=self,
            amount=amount
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
    amount = models.IntegerField()

class Recipe(models.Model):
    pass