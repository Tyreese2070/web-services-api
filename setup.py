import os
import zipfile
import shutil
import django
from django.core.management import call_command
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_recipe.settings')
django.setup()

from django.contrib.auth.models import User

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'dataset')
ZIP_FILE_PATH = os.path.join(BASE_DIR, 'dataset.zip')

def setup_project():
    print("Starting Setup...")

    # download datasets
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    required_files = ['RAW_recipes.csv']
    files_missing = any(not os.path.exists(os.path.join(DATA_DIR, f)) for f in required_files)

    if files_missing:
        # Create dataset folder if it doesn't exist
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

        if os.path.exists(ZIP_FILE_PATH):
            print(f"Found 'dataset.zip'. Extracting to '{DATA_DIR}'...")
            try:
                with zipfile.ZipFile(ZIP_FILE_PATH, 'r') as zip_ref:
                    zip_ref.extractall(DATA_DIR)
                
                # Check for nested dataset folder and fix if exists
                nested_dir = os.path.join(DATA_DIR, 'dataset')
                if os.path.exists(nested_dir) and os.path.isdir(nested_dir):
                    print("Nested folder detected. Moving files...")
                    
                    for filename in os.listdir(nested_dir):
                        source = os.path.join(nested_dir, filename)
                        dest = os.path.join(DATA_DIR, filename)

                        if os.path.exists(dest):
                            os.remove(dest)
                        shutil.move(source, dest)
                    os.rmdir(nested_dir)

                print("Extraction complete.")
            except Exception as e:
                print(f"Error extracting zip: {e}")
                return
        else:
            print(f"Error: 'dataset.zip' not found in {BASE_DIR}")
            print("Please place the zip file in the project root.")
            return
    else:
        print("Data files already exist.")

    # Create database
    print("Creating Database")
    try:
        call_command('migrate', interactive=False)
        print("Tables created.")
    except Exception as e:
        print(f"Failed to create database: {e}")
        return


    # Load recipes
    print("Loading Recipes")
    from api.models import Recipe
    
    # Check if DB is empty
    if Recipe.objects.count() < 100:
        if os.path.exists(os.path.join(DATA_DIR, 'RAW_recipes.csv')):
            try:
                call_command('load_recipes')
            except Exception as e:
                print(f"Error in load_recipes: {e}")
        else:
            print("RAW_recipes.csv missing. Skipping load.")
    else:
        print(f"Database already has {Recipe.objects.count()} recipes.")

    # Create admin user
    print("Creating admin")
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'password123')
        print("User 'admin' created (password: password123)")
    else:
        print("User 'admin' exists.")

    print("\n--------------------------------")
    print("Setup Complete!")
    print("Run: python manage.py runserver")

if __name__ == '__main__':
    setup_project()