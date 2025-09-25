import pytest
from flask import Flask
from recipe.home.home import home_bp
from recipe.recipe_details.recipe_details import recipe_details_bp
from pathlib import Path

@pytest.fixture
def app():
    templates_path = Path(__file__).resolve().parent.parent.parent / 'recipe' / 'templates'
    app = Flask(__name__, template_folder=str(templates_path))
    
    app.register_blueprint(home_bp)
    app.register_blueprint(recipe_details_bp)
    
    return app

def test_homepage_route_found(app):
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 200