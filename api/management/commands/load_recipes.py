import csv
import ast
import os
from django.core.management.base import BaseCommand
from api.models import Recipe, Ingredient

class Command(BaseCommand):
    help = "Load recipes from dataset into database (RAW_recipes.csv)"

    def handle(self, *args, **kwargs):
        # Setup Path
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        file_path = os.path.join(base_dir, 'dataset', 'RAW_recipes.csv')

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File not found: {file_path}"))
            return
        
        # Initialize Buffers
        recipes_buffer = []
        ingredients_cache = set()

        self.stdout.write(f"Reading from {file_path}...")

        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:

                title = row.get("name")
                steps_str = row.get("steps")
                ingredients_str = row.get("ingredients")

                if not title:
                    continue

                try:
                    steps = ast.literal_eval(steps_str)
                    instructions = "\n".join(steps)
                    
                    ingredients_list = ast.literal_eval(ingredients_str)
                    ingredients_json = str(ingredients_list)
                except:
                    continue

                # Add to Buffer
                recipes_buffer.append(Recipe(
                    title=title,
                    instructions=instructions,
                    ingredients=ingredients_json,
                ))

                # Harvest Ingredients
                for ingredient in ingredients_list:
                    ingredients_cache.add(ingredient.strip().lower())

        # save to db
        self.stdout.write(f"Creating {len(recipes_buffer)} recipes...")
        Recipe.objects.bulk_create(recipes_buffer, ignore_conflicts=True)

        self.stdout.write(f"Creating {len(ingredients_cache)} ingredients...")
        existing_names = set(Ingredient.objects.values_list('name', flat=True))
        
        # Only create ingredients that don't exist yet
        new_ingredients = [
            Ingredient(name=ing) 
            for ing in ingredients_cache 
            if ing not in existing_names
        ]
        
        Ingredient.objects.bulk_create(new_ingredients, ignore_conflicts=True)
        
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(recipes_buffer)} recipes and {len(new_ingredients)} new ingredients."))