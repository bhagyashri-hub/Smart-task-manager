"""
app.py - Main entry point for Smart Team Task Manager
Initializes Flask app, extensions, and registers all blueprints.
"""

import os
from flask import Flask
from flask_login import LoginManager
from models import db, User

# ── Blueprint imports ──────────────────────────────────────────────────────────
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.projects import projects_bp
from routes.tasks import tasks_bp
from routes.users import users_bp
from routes.api import api_bp


def create_app():
    """Application factory: creates and configures the Flask app."""
    app = Flask(__name__)

    # ── Configuration ──────────────────────────────────────────────────────────
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'smart-task-manager-secret-2024')

    # SQLite database stored in instance folder
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(basedir, 'taskmanager.db')
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ── Initialize extensions ──────────────────────────────────────────────────
    db.init_app(app)

    # Flask-Login setup
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        """Tell Flask-Login how to reload a user from the session."""
        return User.query.get(int(user_id))

    # ── Register blueprints ────────────────────────────────────────────────────
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    # ── Create tables and seed default admin ───────────────────────────────────
    with app.app_context():
        db.create_all()
        seed_default_admin()

    return app


def seed_default_admin():
    """
    Creates a default admin account on first run if no users exist.
    Credentials: admin / admin123
    """
    from models import User
    if User.query.count() == 0:
        admin = User(username='admin', email='admin@taskmanager.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✅ Default admin created → username: admin | password: admin123")


# ── Run the app ────────────────────────────────────────────────────────────────
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
