import pytest
from flask import Flask
from recipe.recipe_details.recipe_details import recipe_details_bp
from recipe.adapters.memory_repo import MemoryRepository

repo = MemoryRepository()
@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(recipe_details_bp)
    return app

def test_get_recipe_by_id_found():
    recipe = repo.get_recipe(38)
    assert recipe is not None
    assert recipe.name != ""
    assert isinstance(recipe.ingredients, (list, tuple))
    assert isinstance(recipe.ingredient_quantities, (list, tuple))

def test_get_recipe_by_id_not_found():
    recipe = repo.get_recipe(999999)
    assert recipe is None

def test_display_recipe_route_found(app):
    with app.test_client() as client:
        response = client.get('/recipe_details/38')
        assert response.status_code == 200

def test_display_recipe_route_not_found(app):
    with app.test_client() as client:
        response = client.get('/recipe_details/999999')
        assert response.status_code == 404
