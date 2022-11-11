from django.db import models


class Brew(models.Model):
    name = models.CharField(max_length=80)
    date = models.DateField(auto_now=False, auto_now_add=True)

    def __str__(self) -> str:
        return self.date + self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self) -> str:
        return self.name
