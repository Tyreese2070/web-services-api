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
    pass

# Suggest recipes
@api_view(['GET'])
def suggest_recipes(request):
    pass