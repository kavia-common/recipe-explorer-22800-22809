from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db


# Association table for recipe-category many-to-many
recipe_categories = db.Table(
    "recipe_categories",
    db.Column("recipe_id", db.Integer, db.ForeignKey("recipes.id"), primary_key=True),
    db.Column("category_id", db.Integer, db.ForeignKey("categories.id"), primary_key=True),
)

# Association table for favorites (user - recipe)
favorites = db.Table(
    "favorites",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("recipe_id", db.Integer, db.ForeignKey("recipes.id"), primary_key=True),
)


class User(db.Model):
    """User model with password hashing and minimal profile fields."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    recipes = db.relationship("Recipe", backref="author", lazy=True)
    favorite_recipes = db.relationship(
        "Recipe",
        secondary=favorites,
        back_populates="favored_by",
        lazy="dynamic",
    )

    # PUBLIC_INTERFACE
    def set_password(self, password: str) -> None:
        """Set the user's password using secure hashing."""
        self.password_hash = generate_password_hash(password)

    # PUBLIC_INTERFACE
    def check_password(self, password: str) -> bool:
        """Verify the user's password."""
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    """Recipe category."""
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

    recipes = db.relationship(
        "Recipe",
        secondary=recipe_categories,
        back_populates="categories",
        lazy="dynamic",
    )


class Recipe(db.Model):
    """Recipe model with basic fields."""
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    ingredients = db.Column(db.Text, nullable=True)  # newline or comma separated
    instructions = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    categories = db.relationship(
        "Category",
        secondary=recipe_categories,
        back_populates="recipes",
        lazy="dynamic",
    )
    favored_by = db.relationship(
        "User",
        secondary=favorites,
        back_populates="favorite_recipes",
        lazy="dynamic",
    )
