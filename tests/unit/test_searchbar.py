import pytest

from recipe.adapters.memory_repo import MemoryRepository
from recipe.domainmodel.author import Author
from recipe.domainmodel.category import Category
from recipe.domainmodel.recipe import Recipe

@pytest.fixture
def memory_repo():
    repo = MemoryRepository()
    repo._recipes = []
    return repo

@pytest.fixture
def sample_recipes(memory_repo):
    author1 = Author(1, "John Doe")
    author2 = Author(2, "Jane Smith")

    category1 = Category("Beverage")
    category2 = Category("Dessert")
    
    recipe1 = Recipe(
        recipe_id=1,
        name="Mushroom Soup",
        author=author1,
        category=category1
    )
    recipe2 = Recipe(
        recipe_id=2,
        name="Chocolate Cake",
        author=author2,
        category=category2
    )
    recipe3 = Recipe(
        recipe_id=3,
        name="Mushroom Risotto",
        author=author1,
        category=category1
    )

    memory_repo.add_recipe(recipe1)
    memory_repo.add_recipe(recipe2)
    memory_repo.add_recipe(recipe3)

    return [recipe1, recipe2, recipe3]

def test_find_by_name(memory_repo, sample_recipes):
    results = memory_repo.find_by_name("mushroom")
    assert len(results) == 2
    assert sample_recipes[0] in results
    assert sample_recipes[2] in results
    assert sample_recipes[1] not in results

    # Case-insensitive test
    results_upper = memory_repo.find_by_name("MUSHROOM")
    assert len(results_upper) == 2

    # No match
    results_no_match = memory_repo.find_by_name("fadass")
    assert len(results_no_match) == 0
    
def test_find_by_category(memory_repo, sample_recipes):
    results = memory_repo.find_by_category("beverage")
    assert len(results) == 2
    assert sample_recipes[0] in results
    assert sample_recipes[2] in results
    assert sample_recipes[1] not in results

    # Case-insensitive test
    results_upper = memory_repo.find_by_category("BEVERAGE")
    assert len(results_upper) == 2

    # No match
    results_no_match = memory_repo.find_by_category("soup")
    assert len(results_no_match) == 0
    
def test_find_by_author(memory_repo, sample_recipes):
    results = memory_repo.find_by_author("john")
    assert len(results) == 2
    assert sample_recipes[0] in results
    assert sample_recipes[2] in results
    assert sample_recipes[1] not in results

    # Case-insensitive test
    results_upper = memory_repo.find_by_author("JOHN DOE")
    assert len(results_upper) == 2

    # No match
    results_no_match = memory_repo.find_by_author("dadassd")
    assert len(results_no_match) == 0
