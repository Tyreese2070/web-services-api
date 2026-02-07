from django.urls import path
from .views import search_ingredients
urlpatterns = [
    # 1. Search for ingredients (Dropdown)
    path('ingredients/search/', search_ingredients),
]