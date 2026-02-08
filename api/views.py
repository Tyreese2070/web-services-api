from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Recipe, Ingredient, PantryItem
import ast

# Search for ingredients
@api_view(['GET'])
@permission_classes([AllowAny])
def search_ingredients(request):
    """
    Input: /api/ingredients/search/?q=beans
    Output: ["Beans", "Black Beans", "Kidney Beans"]
    """
    query = request.GET.get('q', '')

    if len(query) < 2:
        return Response([])
    
    results = list(Ingredient.objects.filter(name__icontains=query)[:50])

    results.sort(key=lambda x: (
        not x.name.lower().startswith(query),
        len(x.name),
        x.name
    ))

    data = [ingredient.name for ingredient in results]
    return Response(list(data))

# Add to pantry
@api_view(['POST'])
def add_to_pantry(request):
    """
    Input: {"name": "Milk"}
    Action: Add "Milk" to the users pantry
    """
    item_name = request.data.get("name")
    if not item_name:
        return Response({"error": "Name is required"}, status=400)
    
    ingredient, created = Ingredient.objects.get_or_create(name=item_name)
    user = User.objects.filter(is_superuser=True).first() # remove later
    if not user:
        user = User.objects.create_user(username='admin', password='admin', is_superuser=True)

    pantry_item, created = PantryItem.objects.get_or_create(user=user, ingredient=ingredient)

    if created:
        return Response({"message": f"{item_name} added to pantry"}, status=201)
    else:
        return Response({"message": f"{item_name} is already in pantry"}, status=200)

# Suggest recipes
@api_view(['GET'])
def suggest_recipes(request):
    """
    search for recipes containing ingredients in the users pantry
    rank candidates using number of matching ingredients / total ingredients in recipe
    return the top 10 or more then add a load more button
    """
    pass