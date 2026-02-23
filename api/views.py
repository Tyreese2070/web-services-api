from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Q
from django.contrib.auth.models import User
from .models import IngredientInfo, Recipe, Ingredient, PantryItem
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

    pantry_items = PantryItem.objects.all()
    pantry_names = [item.ingredient.name for item in pantry_items]

    if not pantry_names:
        return Response({"error": "Pantry is empty"}, status=200)
    
    # find recipes with a pantry item
    query = Q()
    for name in pantry_names:
        query |= Q(ingredients__icontains=name)

    recipes = Recipe.objects.filter(query)[:200]

    allergen_map = {info.name.lower(): info.allergens for info in IngredientInfo.objects.all() if info.allergens and info.allergens.lower() != "none"}

    recipe_scores = []
    for recipe in recipes:
        try:
            recipe_ingredients = ast.literal_eval(recipe.ingredients)
            recipe_instructions = recipe.instructions.split("\n")
            recipe_ingredients = [i.lower() for i in recipe_ingredients]
        except:
            continue

        matches = [ing for ing in recipe_ingredients if any(p_item in ing for p_item in pantry_names)]
        missing = [ing for ing in recipe_ingredients if ing not in matches]

        if len(recipe_ingredients) > 0:
            match_percentage = (len(matches) / len(recipe_ingredients)) * 100
        else:
            match_percentage = 0

        # Difficulty logic based on the number of steps
        step_count = len(recipe_instructions)
        if step_count < 5:
            difficulty = "Easy"
        elif step_count < 10:
            difficulty = "Medium"
        else:
            difficulty = "Hard"

        # Allergens
        detected_allergens = set()
        for ing in recipe_ingredients:
            for allergen_key, allergen_value in allergen_map.items():
                if allergen_key in ing:
                    detected_allergens.add(allergen_value)
        allergen_list = list(detected_allergens) if detected_allergens else ["None"]

        if match_percentage > 0:
            recipe_scores.append({
                "id": recipe.id,
                "title": recipe.title,
                "difficulty": difficulty,
                "allergens": allergen_list,
                "match_percentage": round(match_percentage, 2),
                "you_have": matches,
                "missing": missing,
                "instructions": recipe_instructions
            })

        recipe_scores.sort(key=lambda x: x['match_percentage'], reverse=True)
        
        return JsonResponse(recipe_scores[:10], safe=False)

 # =================== Webpages ===================
def home(request):
    return render(request, '../frontend/home.html')