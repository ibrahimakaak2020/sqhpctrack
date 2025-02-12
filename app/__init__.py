from datetime import timedelta
from flask import Flask, render_template, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError
from flask_session import Session
from app.config.config import config_dict
import os

from app.db.database import db, init_db, login_manager

csrf = CSRFProtect()

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Security configurations
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    app.config['WTF_CSRF_SECRET_KEY'] = os.environ.get('WTF_CSRF_SECRET_KEY', 'your-csrf-secret-key-here')
    app.config['WTF_CSRF_TIME_LIMIT'] = 3600
    app.config['WTF_CSRF_SSL_STRICT'] = False  # Important for Vercel deployment
    
    # Add CSRF trusted origins
    app.config['WTF_CSRF_TRUSTED_ORIGINS'] = [
        'https://*.vercel.app',  # For Vercel deployments
        'http://localhost:5000',  # For local development
        'http://127.0.0.1:5000',
        'http://172.17.25.165:5000',  # For local development
    ]
    
    # Add your domain when deployed
    if os.environ.get('DOMAIN'):
        app.config['WTF_CSRF_TRUSTED_ORIGINS'].append(
            f"https://{os.environ.get('DOMAIN')}"
        )
    
    # Session configurations
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=20)
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    # Load configuration
    app.config.from_object(config_dict['production'])

    # Initialize the session
    Session(app)

    # Initialize CSRF protection before other extensions
    csrf.init_app(app)

   
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
    init_db(app=app)
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

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))