from flask import Flask
from flask_cors import CORS
from flask_smorest import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from .config import config_by_name

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()

# PUBLIC_INTERFACE
def create_app(config_name: str = "default") -> Flask:
    """Create and configure the Flask application.

    Args:
        config_name: The configuration profile name ('development', 'production', or 'default').

    Returns:
        A configured Flask app instance with registered blueprints and extensions.
    """
    app = Flask(__name__)
    app.url_map.strict_slashes = False

    # Load config
    cfg = config_by_name.get(config_name, config_by_name["default"])
    app.config.from_object(cfg)

    # CORS
    CORS(app, resources={r"/*": {"origins": app.config.get('CORS_ORIGINS', '*')}})

    # API and OpenAPI docs
    app.config["API_TITLE"] = cfg.API_TITLE
    app.config["API_VERSION"] = cfg.API_VERSION
    app.config["OPENAPI_VERSION"] = cfg.OPENAPI_VERSION
    app.config["OPENAPI_SWAGGER_UI_PATH"] = cfg.OPENAPI_SWAGGER_UI_PATH
    app.config["OPENAPI_SWAGGER_UI_URL"] = cfg.OPENAPI_SWAGGER_UI_URL
    app.config["OPENAPI_URL_PREFIX"] = cfg.OPENAPI_URL_PREFIX
    api = Api(app)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)

    # Register blueprints
    from .routes.health import blp as health_blp
    from .routes.auth import blp as auth_blp
    from .routes.recipes import blp as recipes_blp
    from .routes.favorites import blp as favorites_blp

    api.register_blueprint(health_blp)
    api.register_blueprint(auth_blp)
    api.register_blueprint(recipes_blp)
    api.register_blueprint(favorites_blp)

    # Create DB tables if not exist (for demo/local)
    with app.app_context():
        db.create_all()

    return app


# Backwards compatible app/api objects for scripts that import app/app.api
app = create_app()
api = Api(app)
