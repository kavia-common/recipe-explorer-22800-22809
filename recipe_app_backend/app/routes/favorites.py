from flask_smorest import Blueprint
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db
from ..models import Recipe, User
from ..schemas import FavoriteActionSchema, RecipeSchema

blp = Blueprint(
    "Favorites",
    "favorites",
    url_prefix="/favorites",
    description="Mark/unmark and list favorite recipes",
)


@blp.route("")
class FavoriteList(MethodView):
    @jwt_required()
    @blp.response(200, RecipeSchema(many=True))
    def get(self):
        """Get current user's favorite recipes."""
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        # dynamic relationship returns query
        return user.favorite_recipes.order_by(Recipe.created_at.desc()).all()

    @jwt_required()
    @blp.arguments(FavoriteActionSchema)
    def post(self, args):
        """Mark a recipe as favorite for current user."""
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        recipe = Recipe.query.get_or_404(args["recipe_id"])
        if not user.favorite_recipes.filter_by(id=recipe.id).first():
            user.favorite_recipes.append(recipe)
            db.session.commit()
        return {"message": "Marked as favorite"}, 200

    @jwt_required()
    @blp.arguments(FavoriteActionSchema)
    def delete(self, args):
        """Unmark a recipe as favorite for current user."""
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        recipe = Recipe.query.get_or_404(args["recipe_id"])
        if user.favorite_recipes.filter_by(id=recipe.id).first():
            user.favorite_recipes.remove(recipe)
            db.session.commit()
        return {"message": "Removed from favorites"}, 200
