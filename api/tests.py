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
        Test that a user cannot create a new ingredient
        """
        response = self.client.post('/api/pantry/add/', {'name': 'milk'}, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Ingredient 'milk' not recognized")

        # check database
        self.assertFalse(Ingredient.objects.filter(name="milk").exists())
        self.assertFalse(PantryItem.objects.filter(user=self.user, ingredient__name='milk').exists())
    
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

# Authentication Tests
class AuthTests(TestCase):
    """Covers registration, login, logout and account update endpoints."""

    def setUp(self):
        self.client = APIClient()

    def test_register_login_logout_flow(self):
        # registration
        resp = self.client.post('/api/register/', {
            'username': 'alice',
            'password': 'strongpass',
            'first_name': 'Alice',
            'last_name': 'W',
            'email': 'alice@example.com'
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertIn('Success', resp.json())

        # duplicate username
        resp2 = self.client.post('/api/register/', {
            'username': 'alice',
            'password': 'foo',
            'first_name': 'A',
            'last_name': 'B',
            'email': 'other@example.com'
        }, format='json')
        self.assertEqual(resp2.status_code, 400)
        self.assertIn('Username already exists', resp2.json().get('Error', ''))

        # login with wrong credentials
        bad = self.client.post('/api/login/', {'username': 'alice', 'password': 'bad'}, format='json')
        self.assertEqual(bad.status_code, 400)

        # successful login
        login_resp = self.client.post('/api/login/', {'username': 'alice', 'password': 'strongpass'}, format='json')
        self.assertEqual(login_resp.status_code, 200)
        self.assertIn('Logged in successfully', login_resp.json().get('Success', ''))

        # logout
        out = self.client.post('/api/logout/')
        self.assertEqual(out.status_code, 200)
        self.assertIn('Logged out successfully', out.json().get('Success', ''))

    def test_update_account(self):
        # create and login user
        user = User.objects.create_user(username='bob', password='pass123')
        self.client.force_authenticate(user=user)

        # change password but mismatch
        resp = self.client.post('/api/account/update/', {
            'new_password': 'newpass',
            'confirm_password': 'different'
        }, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('Passwords do not match', resp.json().get('error', ''))

        # too short password
        resp2 = self.client.post('/api/account/update/', {
            'new_password': 'short',
            'confirm_password': 'short'
        }, format='json')
        self.assertEqual(resp2.status_code, 400)
        self.assertIn('Password must be longer', resp2.json().get('error', ''))

        # change username to an existing one
        User.objects.create_user(username='charlie', password='xyz')
        resp3 = self.client.post('/api/account/update/', {
            'new_username': 'charlie'
        }, format='json')
        self.assertEqual(resp3.status_code, 400)
        self.assertIn('Username already taken', resp3.json().get('error', ''))

        # valid update
        resp4 = self.client.post('/api/account/update/', {
            'new_username': 'bob2',
            'new_password': 'longenough',
            'confirm_password': 'longenough'
        }, format='json')
        self.assertEqual(resp4.status_code, 200)
        self.assertIn('Account updated successfully', resp4.json().get('success', ''))
        user.refresh_from_db()
        self.assertEqual(user.username, 'bob2')
        self.assertTrue(user.check_password('longenough'))

class PantryManagementTests(TestCase):
    """Tests for adding, updating, and deleting pantry items."""
    def setUp(self):
        self.user = User.objects.create_user(username='pantryuser', password='pwd')
        Ingredient.objects.create(name='egg')
        Ingredient.objects.create(name='flour')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_pantry_empty_then_add(self):
        resp = self.client.get('/api/pantry/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), [])

        response = self.client.post('/api/pantry/add/', {'name': 'egg'}, format='json')
        self.assertEqual(response.status_code, 201)

        get_resp = self.client.get('/api/pantry/')
        self.assertEqual(get_resp.status_code, 200)
        self.assertIn('egg', [item['name'] for item in get_resp.json()])

    def test_update_and_delete_item(self):
        ingredient = Ingredient.objects.get(name='egg')
        PantryItem.objects.create(user=self.user, ingredient=ingredient, quantity='1')

        # update quantity
        upd = self.client.put('/api/pantry/update/', {'name': 'egg', 'quantity': '2'}, format='json')
        self.assertEqual(upd.status_code, 200)
        self.assertIn('quantity updated to 2', upd.json().get('message', ''))

        # attempt to update missing item
        missing = self.client.put('/api/pantry/update/', {'name': 'bread', 'quantity': '1'}, format='json')
        self.assertEqual(missing.status_code, 404)

        # delete existing
        delresp = self.client.delete('/api/pantry/delete/', {'name': 'egg'}, format='json')
        self.assertEqual(delresp.status_code, 200)

        # delete again
        delagain = self.client.delete('/api/pantry/delete/', {'name': 'egg'}, format='json')
        self.assertEqual(delagain.status_code, 404)

class RecipeSuggestionTests(TestCase):
    """Tests for the recipe suggestion endpoint based on pantry contents."""
    def setUp(self):
        self.user = User.objects.create_user(username='chef', password='cook')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # create ingredients and pantry
        ing1 = Ingredient.objects.create(name='tomato')
        ing2 = Ingredient.objects.create(name='cheese')
        PantryItem.objects.create(user=self.user, ingredient=ing1)

        # create recipes
        Recipe.objects.create(
            title='Tomato Soup',
            ingredients="['tomato', 'water']",
            instructions='step1\nstep2'
        )
        Recipe.objects.create(
            title='Cheese Sandwich',
            ingredients="['bread', 'cheese']",
            instructions='make sandwich'
        )

        # allergen info for cheese
        IngredientInfo.objects.create(name='cheese', allergens='dairy')

    def test_suggest_with_pantry(self):
        resp = self.client.get('/api/recipes/suggest/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        # should include Tomato Soup but not Cheese Sandwich (no bread)
        self.assertTrue(any(r['title']=='Tomato Soup' for r in data))
        self.assertFalse(any(r['title']=='Cheese Sandwich' for r in data))

        # limit parameter
        resp2 = self.client.get('/api/recipes/suggest/?limit=1')
        self.assertEqual(len(resp2.json()), 1)

    def test_suggest_empty_pantry(self):
        # remove existing pantry item
        PantryItem.objects.filter(user=self.user).delete()
        resp = self.client.get('/api/recipes/suggest/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('error', resp.json())
        self.assertEqual(resp.json()['error'], 'Pantry is empty')