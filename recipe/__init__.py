"""Initialize Flask app."""
from datetime import datetime
from flask import Flask

def create_app(test_config=None):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev'
    if test_config is not None:
        app.config.update(test_config)

    from .home import home
    app.register_blueprint(home.home_bp)

    from .browse import browse
    app.register_blueprint(browse.browse_bp)

    from .recipe_details import recipe_details
    app.register_blueprint(recipe_details.recipe_details_bp)

    from .authentication import authentication
    app.register_blueprint(authentication.authentication_bp)

    return app

