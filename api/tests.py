from django.test import TestCase
from rest_framework.test import APIClient
from api.models import Ingredient, Recipe
from django.core.management import call_command
from unittest.mock import patch, mock_open
import builtins

# Search for ingredients test
class SearchIngredientsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
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
        # mock data
        csv_content = (
            "name,id,minutes,contributor_id,submitted,tags,nutrition,n_steps,steps,description,ingredients,n_ingredients\n"
            "Test Pasta,123,30,44,2020-01-01,[],[],5,\"['Boil water', 'Cook pasta']\",\"Yummy\",\"['pasta', 'water']\",2"
        )

        original_open = builtins.open

        def open_side_effect(file, mode='r', *args, **kwargs):
            if "RAW_recipes.csv" in str(file):
                return mock_open(read_data=csv_content)(file, mode, *args, **kwargs)
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