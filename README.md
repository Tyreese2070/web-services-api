# Food suggestion API

# Setup
```bash
pip install -r requirements.txt
```

```bash
python setup.py
```

# Running a local server
```bash
python manage.py runserver
```

# Using the live azure site
Visit the website here: [SmartRecipe][link].

[link]: smartrecipeapi-cqeaf6chh5endhan.francecentral-01.azurewebsites.net

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
1.
2.

# Issues
Allergens sometimes appear twice (e.g. "Peanut" and "peanuts")