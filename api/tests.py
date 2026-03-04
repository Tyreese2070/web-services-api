import django
from django.test import TestCase
from rest_framework.test import APIClient
from api.models import Ingredient, IngredientInfo, Recipe, PantryItem
from django.core.management import call_command
from unittest.mock import patch, mock_open
from django.contrib.auth.models import User
import builtins

# Search for ingredients test
class SearchIngredientsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.force_authenticate(user=self.user)
        Ingredient.objects.create(name="apple")
        Ingredient.objects.create(name="pineapple")
        Ingredient.objects.create(name="apple pie")
        Ingredient.objects.create(name="banana")

    def test_filtering_logic(self):
        """
        Test that searching an item returns relevant results only.
        "apple" should return "apple", "apple pie", and "pineapple", but not "banana"
        """
        response = self.client.get('/api/ingredients/search/?q=apple')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("apple", data)
        self.assertIn("apple pie", data)
        self.assertIn("pineapple", data)
        self.assertNotIn("banana", data)

    def test_search_ingredients_short_query(self):
        """
        Test that searching with a short query returns an empty list.
        """
        response = self.client.get('/api/ingredients/search/?q=b')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

class LoadRecipesCommandTests(TestCase):
    def test_load_recipes_command(self):
        """
        Test that the management command parses a CSV row correctly.
        """
        # mock data for recipes
        csv_content = (
            "name,id,minutes,contributor_id,submitted,tags,nutrition,n_steps,steps,description,ingredients,n_ingredients\n"
            "Test Pasta,123,30,44,2020-01-01,[],[],5,\"['Boil water', 'Cook pasta']\",\"Yummy\",\"['pasta', 'water']\",2"
        )

        # mock data for allergens
        allergens_content = (
            "Food Product,Main Ingredient,Allergens\n"
            "pasta,Pasta,Nuts\n"
            "water,Water,None\n"
        )

        original_open = builtins.open

        def open_side_effect(file, mode='r', *args, **kwargs):
            if "RAW_recipes.csv" in str(file):
                return mock_open(read_data=csv_content)(file, mode, *args, **kwargs)
            elif "food_ingredients_and_allergens.csv" in str(file):
                return mock_open(read_data=allergens_content)(file, mode, *args, **kwargs)
            else:
                return original_open(file, mode, *args, **kwargs)

        with patch("builtins.open", side_effect=open_side_effect):
            with patch("os.path.exists", return_value=True):
                
                call_command('load_recipes')

        self.assertEqual(Recipe.objects.count(), 1)
        recipe = Recipe.objects.first()
        self.assertEqual(recipe.title, "Test Pasta")
        self.assertIn("Boil water", recipe.instructions)

        self.assertEqual(Ingredient.objects.count(), 2)
        self.assertTrue(Ingredient.objects.filter(name="pasta").exists())

        # allergen assertions
        self.assertEqual(IngredientInfo.objects.count(), 2)
        self.assertTrue(IngredientInfo.objects.filter(name="pasta").exists())
        self.assertEqual(IngredientInfo.objects.get(name="pasta").allergens, "Nuts")
        self.assertTrue(IngredientInfo.objects.filter(name="water").exists())
        self.assertEqual(IngredientInfo.objects.get(name="water").allergens, "None")

class AddToPantryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_add_new_item(self):
        """
        Test adding a new item to the pantry that doesn't exist in the database
        """
        response = self.client.post('/api/pantry/add/', {'name': 'milk'}, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["message"], "milk added to pantry")

        # check database
        self.assertTrue(Ingredient.objects.filter(name="milk").exists())
        self.assertTrue(PantryItem.objects.filter(user=self.user, ingredient__name='milk').exists())
    
    def test_add_existing_item(self):
        """
        Test adding an item that already exists in the users pantry
        """

        ingredient = Ingredient.objects.create(name="milk")
        PantryItem.objects.create(user=self.user, ingredient=ingredient)

        response = self.client.post('/api/pantry/add/', {'name': 'milk'}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertIn("milk is already in pantry", response.json()['message'])
        
        self.assertEqual(PantryItem.objects.count(), 1)