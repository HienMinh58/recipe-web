import pytest
from recipe.domainmodel.recipe import Recipe
from recipe.adapters.memory_repo import MemoryRepository

@pytest.fixture
def memory_repo():
    repo = MemoryRepository()
    repo.add_recipe(Recipe(1, "Apple Pie", "Author 1"))
    repo.add_recipe(Recipe(2, "Banna Bread", "Author 2"))
    return repo

def test_add_and_get_recipe(memory_repo):
    recipe = Recipe(3, "Carrot Cake", "Author 3")
    memory_repo.add_recipe(recipe)
    assert memory_repo.get_recipe(3) == recipe
    
def test_get_all_recipes(memory_repo):
    recipes = memory_repo.get_all_recipes
    assert len(recipes) == 2
    assert recipes[0].name == "Apple Pie"
    assert recipes[1].name == "Banna Bread"
    
def test_get_nonexistence_recipe(memory_repo):
    assert memory_repo.get_recipe(999) is None

def test_remove_recipe(memory_repo):
    memory_repo.remove_recipe(1)
    assert memory_repo.get_recipe(1) is None
    assert len(memory_repo.get_all_recipes()) == 1
 
