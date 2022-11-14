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
        through='BrewIngredients',
        blank=True
    )

    def __str__(self) -> str:
        return self.created.strftime("%Y-%m-%d %H:%M:%S") + " " + self.name

    def add_ingredient(self, ingredient, amount):
        BrewIngredients.objects.create(
            ingredient=ingredient,
            brew=self,
            amount=amount
        )

class BrewIngredients(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    brew = models.ForeignKey(Brew, on_delete=models.CASCADE)
    amount = models.IntegerField()