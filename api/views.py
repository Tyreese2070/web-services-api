from django.http import JsonResponse
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Case, When, IntegerField, Q
import operator
from functools import reduce
from django.contrib.auth.models import User
from .models import IngredientInfo, Recipe, Ingredient, PantryItem
import ast
import re
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie

# Search for ingredients
@api_view(['GET'])
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
def add_to_pantry(request):
    """
    Input: {"name": "Milk"}
    Action: Add "Milk" to the users pantry
    """
    item_name = request.data.get("name")
    if not item_name:
        return Response({"error": "Name is required"}, status=400)
    
    # Only allow existing ingredients
    ingredient = Ingredient.objects.filter(name__iexact=item_name).first()
    if not ingredient:
        return Response({"error": f"Ingredient '{item_name}' not recognized"}, status=400)
    
    user = request.user
    pantry_item, created = PantryItem.objects.get_or_create(user=user, ingredient=ingredient)

    if created:
        return Response({"message": f"{ingredient.name} added to pantry"}, status=201)
    else:
        return Response({"message": f"{ingredient.name} is already in pantry"}, status=200)

# Suggest recipes
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def suggest_recipes(request):
    """
    search for recipes containing ingredients in the users pantry
    rank candidates using number of matching ingredients / total ingredients in recipe
    return the top recipes up to the limit
    """
    limit = int(request.GET.get('limit', 10))

    pantry_items = PantryItem.objects.filter(user=request.user)
    pantry_names = [item.ingredient.name for item in pantry_items]

    if not pantry_names:
        return Response({"error": "Pantry is empty"}, status=200)
    
    query = Q()
    match_conditions = []
    
    for name in pantry_names:
        query |= Q(ingredients__icontains=name)
        # Give the recipe +1 database point if it contains this specific ingredient
        match_conditions.append(
            Case(When(ingredients__icontains=name, then=1), default=0, output_field=IntegerField())
        )

    if match_conditions:
        # Add up the points for every recipe
        total_matches = reduce(operator.add, match_conditions)
        
        # Filter, score, order by highest score, limit to 200
        recipes = Recipe.objects.filter(query).distinct().annotate(
            match_count=total_matches
        ).order_by('-match_count')[:200]
    else:
        recipes = []

    # Allergens mapping
    common_allergens = {
        "milk": "dairy",
        "cheese": "dairy",
        "butter": "dairy",
        "yogurt": "dairy",
        "cream": "dairy",
        "soy": "soy",
        "soya": "soy",
        "wheat": "wheat",
        "flour": "wheat",
        "bread": "wheat",
        "pasta": "wheat",
        "egg": "egg",
        "eggs": "egg",
        "peanut": "peanut",
        "almond": "tree nut",
        "walnut": "tree nut",
        "cashew": "tree nut",
        "fish": "fish",
        "salmon": "fish",
        "tuna": "fish",
        "shrimp": "shellfish",
        "crab": "shellfish",
        "lobster": "shellfish",
    }

    # Allergens mapping from db (overrides common mapping if exists)
    allergen_map = {**common_allergens}
    for info in IngredientInfo.objects.all():
        if info.allergens and info.allergens.lower() != "none":
            key = info.name.lower().strip()
            allergen_map[key] = info.allergens

    recipe_scores = []
    for recipe in recipes:
        try:
            recipe_ingredients = ast.literal_eval(recipe.ingredients)
            recipe_instructions = recipe.instructions.split("\n")
            recipe_ingredients = [i.lower() for i in recipe_ingredients]
        except:
            continue

        matches = []
        for ing in recipe_ingredients:
            for p_item in pantry_names:
                if p_item in ing:
                    matches.append(ing)
                    break
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
            # check every mapping key as substring
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
    
    # Remove duplicates based on title
    seen = set()
    unique_scores = []
    for score in recipe_scores:
        if score['title'] not in seen:
            unique_scores.append(score)
            seen.add(score['title'])
    
    return JsonResponse(unique_scores[:limit], safe=False)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pantry(request):
    """
    Get the users pantry items
    """
    user = request.user
    pantry_items = PantryItem.objects.filter(user=user)
    data = [{"name": item.ingredient.name, "quantity": item.quantity} for item in pantry_items]
    return Response(data, status=200)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_pantry_item(request):
    """
    Update the quantity of a pantry item
    """
    item_name = request.data.get("name")
    quantity = request.data.get("quantity")

    if not item_name or quantity is None:
        return Response({"error": "Name and quantity are required"}, status=400)
    try:
        pantry_item = PantryItem.objects.get(user=request.user, ingredient__name=item_name)
        pantry_item.quantity = quantity
        pantry_item.save()
        return Response({"message": f"{item_name} quantity updated to {quantity}"}, status=200)
    except PantryItem.DoesNotExist:
        return Response({"error": f"{item_name} not found in pantry"}, status=404)
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_pantry_item(request):
    """
    Delete a pantry item
    """
    item_name = request.data.get("name")

    if not item_name:
        return Response({"error": "Name is required"}, status=400)
    try:
        pantry_item = PantryItem.objects.get(user=request.user, ingredient__name=item_name)
        pantry_item.delete()
        return Response({"message": f"{item_name} removed from pantry"}, status=200)
    except PantryItem.DoesNotExist:
        return Response({"error": f"{item_name} not found in pantry"}, status=404)

 # =================== Webpages ===================
@login_required(login_url='/login/')
def home(request):
    return render(request, '../frontend/templates/home.html', {'user': request.user})

@ensure_csrf_cookie
def login_page(request):
    """Login page"""
    return render(request, '../frontend/templates/login.html')

@ensure_csrf_cookie
def register_page(request):
    """Register page"""
    return render(request, '../frontend/templates/register.html')

@login_required(login_url='/login/')
def account_page(request):
    """Account details page"""
    return render(request, '../frontend/templates/account.html')

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    email = request.data.get('email')

    if not username or not password or not first_name or not last_name or not email:
        return Response({"Error": "All fields are required"}, status=400)
    if User.objects.filter(username=username).exists():
        return Response({"Error": "Username already exists"}, status=400)
    if User.objects.filter(email=email).exists():
        return Response({"Error": "Email already registered"}, status=400)
    
    user = User.objects.create_user(
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
        email=email
    )
    return Response({"Success": "User registered successfully"}, status=201)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return Response({"Success": "Logged in successfully"}, status=200)
    else:
        return Response({"Error": "Incorrect username or password"}, status=400)
    
@api_view(['POST'])
def logout_user(request):
    logout(request)
    return Response(({"Success": "Logged out successfully"}), status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_account(request):
    new_username = request.data.get('new_username')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')

    if new_password and new_password != confirm_password:
        return Response({"error": "Passwords do not match"}, status=400)
    if new_password and len(new_password) <= 6:
        return Response({"error": "Password must be longer than 6 characters"}, status=400)
    
    user = request.user
    if new_username and new_username != user.username:
        if User.objects.filter(username=new_username).exists():
            return Response({"error": "Username already taken"}, status=400)
        user.username = new_username
    if new_password:
        user.set_password(new_password)
    user.save()
    return Response({"success": "Account updated successfully"}, status=200)