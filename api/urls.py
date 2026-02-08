from django.urls import path
from .views import search_ingredients, add_to_pantry, suggest_recipes
urlpatterns = [
    # 1. Search for ingredients (Dropdown)
    path('ingredients/search/', search_ingredients),
    path('pantry/add/', add_to_pantry),
    path('recipes/suggest/', suggest_recipes),
]