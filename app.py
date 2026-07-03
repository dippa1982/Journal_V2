import os

from flask import Flask

from extensions import (
    db,
    login_manager,
    migrate
)

# Blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.journal import journal_bp
from routes.calendar import calendar_bp
from routes.insights import insights_bp
from routes.settings import settings_bp
from routes.export import export_bp


def create_app():

    app = Flask(__name__)

    # ----------------------------
    # Configuration
    # ----------------------------

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL",
        "sqlite:///journal.db"
    )

    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY",
        "local-development-key"
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ----------------------------
    # Extensions
    # ----------------------------

    db.init_app(app)

    login_manager.init_app(app)

    migrate.init_app(app, db)

    login_manager.login_view = "auth.login"

    # ----------------------------
    # Blueprints
    # ----------------------------

    app.register_blueprint(auth_bp)

    app.register_blueprint(dashboard_bp)

    app.register_blueprint(journal_bp)

    app.register_blueprint(calendar_bp)

    app.register_blueprint(insights_bp)

    app.register_blueprint(settings_bp)

    app.register_blueprint(export_bp)

    return app


app = create_app()

if __name__ == "__main__":

    app.run(debug=True)