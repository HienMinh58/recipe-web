import pytest
from flask_paginate import Pagination

from recipe.adapters.datareader.csvdatareader import CSVDataReader
from recipe.browse.browse import browse
from recipe.domainmodel.recipe import Recipe

@pytest.fixture
def sample_recipe():
    return [Recipe(1, "Apple", "Author1"),
            Recipe(2, "Banana", "Author2"),
            Recipe(3, "Muffins", "Author3")
    ]

def test_sort_by_name(sample_recipe):
    sample_recipe.sort(key=lambda r: r.name.lower())
    assert [r.name for r in sample_recipe] == ["Apple", "Banana", "Muffins"]

@pytest.fixture
def sample_recipe_1():
    return [Recipe(i, f"Recipe {i}", f"Author {i}") for i in range(1, 16)]

def test_pagination(sample_recipe_1):
    paginated = sample_recipe_1[0:10]
    assert len(paginated) == 10
    assert paginated[0].name == "Recipe 1"
    assert paginated[-1].name == "Recipe 10"
    
    paginated = sample_recipe_1[10:15]
    assert len(paginated) == 5
    assert paginated[0].name == "Recipe 11"
    assert paginated[-1].name == "Recipe 15"
    
    paginated = sample_recipe_1[20:30]
    assert len(paginated) == 0    
