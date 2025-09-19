# Recipe App Backend (Flask)

Features:
- Flask + SQLAlchemy + JWT auth
- Recipes CRUD
- Search by text, ingredients, categories
- Favorites (mark/unmark, list)
- OpenAPI docs with flask-smorest at /docs
- Seed data for quick testing

Quick start:
1) Install deps: `pip install -r requirements.txt`
2) Run the app: `python run.py`
3) Docs: visit `/docs` on the backend URL
4) Seed demo data (optional): 
   - Open a python shell:
     ```
     from app import app, db
     from app.seed import seed_data
     with app.app_context():
         db.create_all()
         seed_data()
     ```
   - Login with demo user:
     - email: demo@example.com
     - password: password123

Environment variables:
- SECRET_KEY
- JWT_SECRET_KEY
- DATABASE_URL (default sqlite:///recipe_app.db)
- CORS_ORIGINS

API Overview:
- GET / -> health
- POST /auth/signup
- POST /auth/login -> returns access_token
- GET /auth/me (JWT)
- PATCH /auth/me (JWT)
- GET /recipes
- POST /recipes (JWT)
- GET /recipes/{id}
- PATCH /recipes/{id} (JWT, author only)
- DELETE /recipes/{id} (JWT, author only)
- GET /recipes/categories
- GET /favorites (JWT)
- POST /favorites (JWT) body: {"recipe_id": number}
- DELETE /favorites (JWT) body: {"recipe_id": number}
