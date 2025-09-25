from recipe.adapters.datareader.csvdatareader import CSVDataReader

from recipe.domainmodel.user import User
from recipe.domainmodel.recipe import Recipe
from recipe.domainmodel.review import Review
from recipe.domainmodel.favourite import Favourite


class MemoryRepository:
    def __init__(self):
        self._users = []
        self._recipes = []
        self._reviews = {}
        self._favourites = []
        self.read_all_recipes('recipe/adapters/data/recipes.csv')
    
    def add_user(self, user : User):
        self._users.append(user)
    
    def get_user(self, username: str):
        return next((u for u in self._users if u.username == username), None)
    
    def add_recipe(self, recipe : Recipe):
        self._recipes.append(recipe)
    
    def get_recipe(self, recipe_id : int):
        return next((r for r in self._recipes if r.id == recipe_id), None)

    def read_all_recipes(self, csv_path : str):
        reader = CSVDataReader(csv_path)
        reader.csv_reader()
        self._recipes = reader.recipes

    def get_all_recipes(self):
        return list(self._recipes)

    def add_review(self, review : Review):
        recipe_id = review.recipe_id
        if recipe_id not in self._reviews:
            self._reviews[recipe_id] = []
        self._reviews[recipe_id].append(review)
    
    def get_reviews_for_recipe(self, recipe_id : int):
        return sorted(self._reviews.get(recipe_id, []), key=lambda r: r.date_submitted, reverse=True)
    
    def add_favourite(self, favourite : Favourite):
        self._favourites.append(favourite)

    def get_favourites_for_user(self, user_id : int):
        return [f for f in self._favourites if f.user.id == user_id]
    
    def find_by_name(self, query: str):
        return [r for r in self._recipes if query.lower() in r.name.lower()]

    def find_by_category(self, query: str):
        return [r for r in self._recipes if query.lower() in r.category.name.lower()]
    
    def find_by_author(self, query: str):
        return [r for r in self._recipes if query.lower() in r.author.name.lower()]
    
        


