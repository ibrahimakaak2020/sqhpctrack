from datetime import timedelta
from flask import Flask, render_template, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError
from flask_session import Session
import os

from app.config.config import Config, ProductionConfig
from app.db.database import db, init_db, login_manager

csrf = CSRFProtect()

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Database Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    #app.config['SQLALCHEMY_ECHO'] = True  # Set to False in production
    
    # Security configurations
    app.config.update(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-key-please-change'),
        WTF_CSRF_ENABLED=True,
        WTF_CSRF_SECRET_KEY=os.environ.get('WTF_CSRF_SECRET_KEY', 'csrf-key-please-change'),
        WTF_CSRF_TIME_LIMIT=3600,
        WTF_CSRF_SSL_STRICT=False,
        WTF_CSRF_CHECK_DEFAULT=True,
        SESSION_COOKIE_SECURE=False,  # Set to True in production
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_DOMAIN=None,
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=60)
    )
    
    # Session configurations
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = True

    # Initialize extensions
    Session(app)
    csrf.init_app(app)
    init_db(app=app)
    login_manager.init_app(app)
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    # Initialize extensions
   
    login_manager.init_app(app)
    login_manager.login_view = 'users.login'
    login_manager.login_message_category = 'info'

    # CSRF error handler
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('errors/csrf_error.html', reason=e.description), 400

    with app.app_context():
        # Import models to ensure tables are created
        from .models import User, CompanyUser, Workshop, Equipment, MaintenanceRecord, MaintenanceStatus
        from .routers.main import main_bp as main_router
        from .routers.user_routes import users_bp as user_blueprint
        from .routers.company_routes import company_bp as company_blueprint
        from .routers.workshop_routes import workshop_bp as workshop_blueprint
        from .routers.equipment import equipment_bp as equipment_blueprint
        
        # Exempt routes using csrf.exempt decorator
      
        
        # Register blueprints
        app.register_blueprint(equipment_blueprint, url_prefix='/equipment')
        app.register_blueprint(main_router)
        app.register_blueprint(user_blueprint, url_prefix='/users')
        app.register_blueprint(company_blueprint, url_prefix='/companies')
        app.register_blueprint(workshop_blueprint, url_prefix='/workshops')
   
     
     
        # Create all tables
        db.create_all()

    return app

class CustomProductionConfig(ProductionConfig):
    # Basic Flask settings
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    
    # Security settings
    TALISMAN_ENABLED = False
    HTTP_HEADERS = {
        "X-Frame-Options": "ALLOWALL",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, X-CSRF-Token"
    }
    
    # CORS settings
    ENABLE_CORS = True
    CORS_OPTIONS = {
        "supports_credentials": True,
        "allow_headers": ["Content-Type", "X-CSRF-Token"],
        "expose_headers": ["Content-Type", "X-CSRF-Token"],
        "resources": r"/*",
        "origins": [
            "http://localhost:5000",
            "http://127.0.0.1:5000",
            "https://*.vercel.app",
            "https://sqhpctrack.vercel.app",
            "*"  # Remove in production
        ]
    }
    
    # CSRF settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY', 'your-csrf-secret-key')
    WTF_CSRF_CHECK_DEFAULT = True
    WTF_CSRF_SSL_STRICT = False
    WTF_CSRF_TIME_LIMIT = 3600
    WTF_CSRF_TRUSTED_ORIGINS = [
        'http://localhost:5000',
        'http://127.0.0.1:5000',
        'https://*.vercel.app',
        'https://sqhpctrack.vercel.app'
    ]
    
    # Proxy settings
    ENABLE_PROXY_FIX = True
    PROXY_FIX_CONFIG = {
        "x_for": 1,
        "x_proto": 1,
        "x_host": 1,
        "x_port": 1,
        "x_prefix": 1
    }
    
    # Session settings
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    SESSION_COOKIE_SECURE = False  # Set to True in production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_NAME = 'session'
    SESSION_COOKIE_DOMAIN = None

    # Cache settings
    CACHE_CONFIG = {
        'CACHE_TYPE': 'simple',
        'CACHE_DEFAULT_TIMEOUT': 300
    }
    DATA_CACHE_CONFIG = CACHE_CONFIG

app = create_app(CustomProductionConfig)



@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))