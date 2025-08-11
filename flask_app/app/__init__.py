import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from dotenv import load_dotenv

# Initialize extensions
db = SQLAlchemy()


def create_app():
    load_dotenv()
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Database configuration
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/automation_db",
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Init extensions
    db.init_app(app)

    # Register blueprints/routes
    from .routes import api_bp

    app.register_blueprint(api_bp)

    # Create tables and seed demo data on first run
    with app.app_context():
        from .models import (
            RequestModel,
            ActionModel,
            Environment,
            EnvironmentVariable,
            Snippet,
            Scenario,
            ScenarioStep,
        )

        db.create_all()
        # Seed only if empty
        env_count = db.session.execute(text("SELECT COUNT(*) FROM environment")).scalar()
        if env_count == 0:
            from .seed import seed_demo_data

            seed_demo_data()

    return app
