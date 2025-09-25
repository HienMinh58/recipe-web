import os
import csv
import ast
from datetime import datetime
from recipe.domainmodel.author import Author
from recipe.domainmodel.category import Category
from recipe.domainmodel.nutrition import Nutrition
from recipe.domainmodel.recipe import Recipe


class CSVDataReader:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.recipes = []
        self.authors = {}
        self.categories = {}
        self.nutritions = []

    def csv_reader(self):
        with open(self.csv_path, encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:

                #author
                author_id = int(row['AuthorId'])
                author_name = row['AuthorName']
                if author_id not in self.authors:
                    author = Author(author_id, author_name)
                    self.authors[author_id] = author
                else:
                    author = self.authors[author_id]

                #category
                category_name = row['RecipeCategory']
                if category_name not in self.categories:
                    category = Category(category_name)
                    self.categories[category_name] = category
                else:
                    category = self.categories[category_name]

                #nutrition
                nutrition = Nutrition(
                    recipe_id = int(row['RecipeId']),
                    calories = float(row['Calories']),
                    fat = float(row['FatContent']),
                    saturated_fat = float(row['SaturatedFatContent']),
                    cholesterol = float(row['CholesterolContent']),
                    sodium = float(row['SodiumContent']),
                    carbohydrates = float(row['CarbohydrateContent']),
                    fiber = float(row['FiberContent']),
                    sugar = float(row['SugarContent']),
                    protein = float(row['ProteinContent']),
                )
                self.nutritions.append(nutrition)
                # Parse optional fields
                try:
                    created_date = datetime.strptime(row['DatePublished'], "%dth %b %Y")
                except Exception:
                    created_date = None
                try:
                    images = ast.literal_eval(row['Images'])
                except Exception:
                    images = []
                try:
                    ingredient_quantities = ast.literal_eval(row['RecipeIngredientQuantities'])
                except Exception:
                    ingredient_quantities = []
                try:
                    ingredients = ast.literal_eval(row['RecipeIngredientParts'])
                except Exception:
                    ingredients = []
                try:
                    instructions = ast.literal_eval(row['RecipeInstructions'])
                except Exception:
                    instructions = []

                #recipe
                recipe = Recipe(
                    int(row['RecipeId']),
                    row['Name'],
                    author=author,
                    cook_time=int(row['CookTime']) if row['CookTime'] else 0,
                    preparation_time=int(row['PrepTime']) if row['PrepTime'] else 0,
                    created_date=created_date,
                    description=row['Description'],
                    images=images,
                    category=category,
                    ingredient_quantities=ingredient_quantities,
                    ingredients=ingredients,
                    nutrition=nutrition,
                    servings=row.get('RecipeServings', None),
                    recipe_yield=row.get('RecipeYield', None),
                    instructions=instructions
                )
                self.recipes.append(recipe)
                author.add_recipe(recipe)
