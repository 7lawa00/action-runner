import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy import text
from dotenv import load_dotenv

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()


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
    login_manager.init_app(app)
    login_manager.login_view = 'api.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))

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
            User,
            DatabaseConnection,
            TestCase,
            TestSuite,
            TestSuiteCase,
            TestCaseShare,
            TestSuiteShare,
            SeleniumAction,
            SQLQuery,
        )

        db.create_all()
        # Seed only if empty
        env_count = db.session.execute(text("SELECT COUNT(*) FROM environment")).scalar()
        if env_count == 0:
            from .seed import seed_demo_data

            seed_demo_data()

    return app
