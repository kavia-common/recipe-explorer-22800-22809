from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, and_
from .. import db
from ..models import Recipe, Category
from ..schemas import (
    RecipeSchema,
    RecipeCreateUpdateSchema,
    PaginationSchema,
    CategorySchema,
)

blp = Blueprint(
    "Recipes",
    "recipes",
    url_prefix="/recipes",
    description="Manage and search recipes",
)


def _get_or_create_categories(names: list[str]) -> list[Category]:
    """Get Category instances for given names; create any missing."""
    cats = []
    for n in names:
        n = n.strip()
        if not n:
            continue
        c = Category.query.filter(Category.name.ilike(n)).first()
        if not c:
            c = Category(name=n)
            db.session.add(c)
        cats.append(c)
    return cats


@blp.route("")
class RecipeList(MethodView):
    @blp.arguments(PaginationSchema, location="query")
    @blp.response(200, RecipeSchema(many=True))
    def get(self, pagination_args):
        """List recipes with optional search by 'q', 'ingredients', 'categories'.
        ---
        summary: List and search recipes
        description: >
          Search recipes by title/description (q), ingredients (comma separated),
          or categories (comma separated). Supports pagination.
        tags:
          - Recipes
        parameters:
          - in: query
            name: q
            schema:
              type: string
            description: Query for title/description
          - in: query
            name: ingredients
            schema:
              type: string
            description: Comma separated ingredients to search
          - in: query
            name: categories
            schema:
              type: string
            description: Comma separated category names
        """
        q = request.args.get("q", type=str)
        ingredients = request.args.get("ingredients", type=str)
        categories = request.args.get("categories", type=str)

        page = pagination_args.get("page", 1)
        per_page = pagination_args.get("per_page", 10)

        query = Recipe.query

        if q:
            ilike = f"%{q}%"
            query = query.filter(or_(Recipe.title.ilike(ilike), Recipe.description.ilike(ilike)))

        if ingredients:
            parts = [p.strip() for p in ingredients.split(",") if p.strip()]
            if parts:
                conds = [Recipe.ingredients.ilike(f"%{p}%") for p in parts]
                query = query.filter(and_(*conds))

        if categories:
            names = [c.strip() for c in categories.split(",") if c.strip()]
            if names:
                query = query.join(Recipe.categories).filter(Category.name.in_(names))

        items = query.order_by(Recipe.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        return items.items

    @jwt_required()
    @blp.arguments(RecipeCreateUpdateSchema)
    @blp.response(201, RecipeSchema)
    def post(self, args):
        """Create a new recipe for the authenticated user.
        ---
        summary: Create recipe
        tags:
          - Recipes
        """
        user_id = get_jwt_identity()
        recipe = Recipe(
            title=args["title"],
            description=args.get("description"),
            ingredients=args.get("ingredients"),
            instructions=args.get("instructions"),
            author_id=user_id,
        )
        category_names = args.get("category_names", [])
        cats = _get_or_create_categories(category_names)
        for c in cats:
            recipe.categories.append(c)
        db.session.add(recipe)
        db.session.commit()
        return recipe


@blp.route("/<int:recipe_id>")
class RecipeDetail(MethodView):
    @blp.response(200, RecipeSchema)
    def get(self, recipe_id: int):
        """Get a single recipe by ID."""
        recipe = Recipe.query.get_or_404(recipe_id)
        return recipe

    @jwt_required()
    @blp.arguments(RecipeCreateUpdateSchema(partial=True))
    @blp.response(200, RecipeSchema)
    def patch(self, args, recipe_id: int):
        """Update a recipe. Only author can update."""
        user_id = get_jwt_identity()
        recipe = Recipe.query.get_or_404(recipe_id)
        if recipe.author_id != user_id:
            return {"message": "Not allowed"}, 403

        for field in ["title", "description", "ingredients", "instructions"]:
            if field in args and args[field] is not None:
                setattr(recipe, field, args[field])

        if "category_names" in args:
            # replace categories
            recipe.categories = []
            cats = _get_or_create_categories(args.get("category_names") or [])
            for c in cats:
                recipe.categories.append(c)

        db.session.commit()
        return recipe

    @jwt_required()
    def delete(self, recipe_id: int):
        """Delete a recipe. Only author can delete."""
        user_id = get_jwt_identity()
        recipe = Recipe.query.get_or_404(recipe_id)
        if recipe.author_id != user_id:
            return {"message": "Not allowed"}, 403
        db.session.delete(recipe)
        db.session.commit()
        return {"message": "Deleted"}, 200


@blp.route("/categories")
class CategoryList(MethodView):
    @blp.response(200, CategorySchema(many=True))
    def get(self):
        """List all categories."""
        return Category.query.order_by(Category.name.asc()).all()
