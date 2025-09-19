import os
from app import create_app

if __name__ == "__main__":
    env = os.getenv("FLASK_ENV", "development")
    app = create_app("production" if env == "production" else "development")
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
