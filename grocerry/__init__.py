import os
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_restful import Api
import logging

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

# Name of the database file
DB_NAME = 'database.db'

def create_app():
    """Application Factory to create and configure Flask app."""
    app = Flask(__name__)

    # Configurations
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///' + DB_NAME)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from .views import views
    from .auth import auth
    from .api import api_bp

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Logging setup
    setup_logging(app)

    # Initialize database
    with app.app_context():
        db.create_all()

    # Login manager setup
    login_manager = LoginManager()
    login_manager.login_view = 'auth.user_login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        """Loads a user by ID for Flask-Login."""
        from .models import User
        return User.query.get(int(id))

    @login_manager.unauthorized_handler
    def unauthorized():
        """Redirect unauthorized users to login."""
        app.logger.warning('Unauthorized access attempt detected.')
        return redirect(url_for('auth.user_login')), 403

    return app

def setup_logging(app):
    """Sets up logging for the application."""
    logging.basicConfig(filename='app.log', level=logging.INFO)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Application Startup')

def create_database(app):
    """Creates the database file if it doesn't exist."""
    if not os.path.exists('grocery/' + DB_NAME):
        with app.app_context():
            db.create_all()
        print('Created Database!')
