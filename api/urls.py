from django.urls import path
from .views import delete_pantry_item,get_pantry, update_pantry_item, search_ingredients, add_to_pantry, suggest_recipes, login_user, logout_user, register_user, update_account
urlpatterns = [
    path('ingredients/search/', search_ingredients),
    path('pantry/add/', add_to_pantry),
    path('recipes/suggest/', suggest_recipes),
    path('login/', login_user),
    path('register/', register_user),
    path('logout/', logout_user),
    path('pantry/', get_pantry),
    path('pantry/update/', update_pantry_item),
    path('pantry/delete/', delete_pantry_item),
    path('account/update/', update_account)
]