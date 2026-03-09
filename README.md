# Food suggestion API
# API Documentation
[View API Documentation](./docs/api_docs.pdf)

Note: If you cannot view the pdf, there is also a markdown version in the same directory.

# Setup
Python 3.10 is required to use /admin dashboard without errors.

Python 3.10 or later can be used just to use the site. Remove 3.10 from the venv initialisation to use the current version of python on your computer.

```bash
git clone https://github.com/Tyreese2070/web-services-api.git
cd web-services-api

# For Windows:
py -3.10 -m venv .venv
.venv\Scripts\activate

# For Mac/Linux:
python3.10 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
python setup.py
```

# Running a local server
```bash
python manage.py runserver
```

The terminal should say that it has started a development server, visit that link to view the site.

Example:

```Starting development server at http://127.0.0.1:8000/```

# Using the live azure site
Visit the website here: https://smartrecipeapi-cqeaf6chh5endhan.francecentral-01.azurewebsites.net

# Usage

## Login and Registration
Users can make an account for their own personal pantry to keep track of what they have, and to find recipes with the ingredients in their pantry.

![login image](/README-images/login.png)

## Managing your Pantry
Users can add items from a large list of ingredients gathered from the recipes to their pantry.

![pantry dropdown image](/README-images/add_to_pantry.png)

You can change the quantity of an ingredient in your pantry to keep track of what you currently have, or you can remove ingredients.

![manage pantry example image](/README-images/manage_pantry.png)

## Finding a Recipe
Pressing "find recipes" finds the best match based on the items in your pantry, it is sorted by the total number of matching ingredients from the pantry and the required ingredients for the recipe.

Each recipe card contains the required ingredients seperated into ones you have and ingredients that are missing, the instructions to cook the recipe, the difficulty, and the potential allergens within that recipe.

The difficulty is based on the number of steps required to cook.

![recipe cards image](/README-images/recipe_cards.png)

## Managing an account

Users can logout or update their username or password by pressing one of the buttons on the top navigation menu.

# Dataset Sources
1. Recipes and ingredients: https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions

2. Allergens: https://www.kaggle.com/datasets/uom190346a/food-ingredients-and-allergens

# Issues
Allergens sometimes appear twice (e.g. "Peanut" and "peanuts")