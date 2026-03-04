from django.urls import path
from .views import search_ingredients, add_to_pantry, suggest_recipes, login_user, logout_user, register_user
urlpatterns = [
    path('ingredients/search/', search_ingredients),
    path('pantry/add/', add_to_pantry),
    path('recipes/suggest/', suggest_recipes),
    path('login/', login_user),
    path('register/', register_user),
    path('logout/', logout_user),
]