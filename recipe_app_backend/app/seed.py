from . import db
from .models import User, Category, Recipe


# PUBLIC_INTERFACE
def seed_data():
    """Seed the database with basic users, categories, and recipes for testing."""
    # Ensure demo user exists
    demo = User.query.filter_by(email="demo@example.com").first()
    if not demo:
        demo = User(email="demo@example.com", name="Demo User")
        demo.set_password("password123")
        db.session.add(demo)
        db.session.flush()  # Ensure demo.id is available

    # Ensure categories exist
    cat_names = ["Breakfast", "Lunch", "Dinner", "Dessert", "Vegan", "Quick"]
    cats_by_name = {}
    for n in cat_names:
        c = Category.query.filter_by(name=n).first()
        if not c:
            c = Category(name=n)
            db.session.add(c)
        cats_by_name[n] = c

    # Add initial recipes only if none exist
    if Recipe.query.count() == 0:
        r1 = Recipe(
            title="Avocado Toast",
            description="Crispy toast with smashed avocado and chili flakes.",
            ingredients="Bread, Avocado, Salt, Chili Flakes, Olive Oil",
            instructions="Toast bread. Smash avocado with salt and olive oil. Spread and top with chili flakes.",
            author_id=demo.id,
        )
        r1.categories.extend([cats_by_name["Breakfast"], cats_by_name["Quick"]])

        r2 = Recipe(
            title="Vegan Buddha Bowl",
            description="A nourishing bowl with quinoa, roasted veggies, and tahini.",
            ingredients="Quinoa, Sweet Potato, Chickpeas, Spinach, Tahini, Lemon",
            instructions="Cook quinoa. Roast sweet potatoes and chickpeas. Assemble with spinach and tahini dressing.",
            author_id=demo.id,
        )
        r2.categories.extend([cats_by_name["Lunch"], cats_by_name["Vegan"]])

        db.session.add_all([r1, r2])

    # Finalize changes
    db.session.commit()
