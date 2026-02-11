from django.urls import path
from .views import home, search_ingredients, add_to_pantry, suggest_recipes
urlpatterns = [
    path('ingredients/search/', search_ingredients),
    path('pantry/add/', add_to_pantry),
    path('recipes/suggest/', suggest_recipes),
    path('', home, name='home'),
]