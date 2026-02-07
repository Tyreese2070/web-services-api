# Food suggestion API

## Data
1. epiRecipes for recipes, includes an ingredients list: https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions

2. food.com interactions to calculate a rating for each recipe: https://www.kaggle.com/datasets/hugodarwood/epirecipes

## Database
Table 1: Ingredients - list of standardised ingredient names (e.g id:50, name: "garlic")

Table 2: recipes - title, instructions and rating.

Table 3: recipe ingredients - many to many (link recipe id to ingredient id)

Table 4: user pantry - CRUD store, link user id to ingredient id. Let the user update what they have

## GenAI
Use ollama to extract base ingredients from a recipe.
Example "3 cloves of garlic, minced" should just store "garlic"

## API endpoints
1. READ - GET /recommendations: finds recipes where the user owns the highest percentage of ingredients. Use ratings as a tie breaker or for a display order.

2. CREATE - POST /pantry: accept a string, processed through ollama and added to the user's inventory.

3. UPDATE - PATCH /pantry/{item_id}: allows the user to change quantity or remove items from pantry

4. DELETE - DELETE /pantry/{item_id} removes item from pantry once cooked or used

# Extra
* use async def
* automated testing - github actions?
* Swagger documentation
* error handling