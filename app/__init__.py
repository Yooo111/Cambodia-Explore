from flask import Flask, render_template
from config import Config
from extensions import db, csrf, login_manager


def create_app(config_class=Config):
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(config_class)

    # Init extensions
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    # Flask-Login settings
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"

    # Import models (so db.create_all() sees them)
    from app.models import (
        UserTable, RoleTable, PermissionTable, Location,
        RuleTable, FactTable, TagTable, MoodTable, GoWithTable, TaxonomyTable
    )
    from app.services.seed_service import seed_database

    # Flask-Login: load user by ID
    @login_manager.user_loader
    def load_user(user_id: str):
        return UserTable.query.get(int(user_id))

    # Register blueprints
    from app.explorer import explorer_bp
    from app.admin import admin_bp
    from app.auth import auth_bp

    app.register_blueprint(explorer_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)

    # Custom Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    # Create tables and seed data
    with app.app_context():
        db.create_all()
        seed_database()

    return app

# Expose WSGI application instance so `gunicorn app:app` finds `app` in package `app`
app = create_app()



