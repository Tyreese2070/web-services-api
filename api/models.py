from django.db import models
from django.contrib.auth.models import User

class Ingredient(models.Model):
    """
    Store ingredient names and categories.
    """

    name = models.CharField(max_length=255, unique=True)
    category = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

class PantryItem(models.Model):
    """
    Store user-specific pantry items, linking to the Ingredient model
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.quantity} of {self.ingredient.name} for {self.user.username}"
    
class Recipe(models.Model):
    """
    Store recipe information, including title, ingredients, and instructions.
    """

    title = models.CharField(max_length=255)
    ingredients = models.TextField()
    instructions = models.TextField()

    def __str__(self):
        return self.title

class IngredientInfo(models.Model):
    """
    Store information about ingredients
    """
    name = models.CharField(max_length=255, unique=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    allergens = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.allergens})"