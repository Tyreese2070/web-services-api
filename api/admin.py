from django.contrib import admin
from .models import Ingredient, PantryItem, Recipe

admin.site.register(Ingredient)
admin.site.register(PantryItem)
admin.site.register(Recipe)
