from datetime import timedelta
from flask import Flask, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_session import Session
from app.config.config import config_dict

from  app.db.database import db,init_db,login_manager

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=20)

# Initialize the session
    Session(app)

    @app.before_request
    def make_session_permanent():
        session.permanent = True
  
    @app.errorhandler(404)
    def not_found_error(error):
     
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
    
        return render_template('errors/403.html'), 403 
    # Load configuration
    app.config.from_object(config_dict[config_name])
    
    init_db(app=app)
    login_manager.login_view = 'users.login'  # Specify the login route
    login_manager.login_message_category = 'info'
    
    csrf = CSRFProtect(app)
    
    with app.app_context():
        # Import models to ensure tables are created
        from .models import User, CompanyUser, Workshop, Equipment, MaintenanceRecord, MaintenanceStatus
        from .routers.main   import main_bp as main_router
        from .routers.user_routes import users_bp as user_blueprint
        from .routers.company_routes import company_bp as company_blueprint
        from .routers.workshop_routes import workshop_bp as workshop_blueprint
        from .routers.equipment import equipment_bp as equipment_blueprint
        app.register_blueprint(equipment_blueprint, url_prefix='/equipment')
        app.register_blueprint(main_router)
        app.register_blueprint(user_blueprint, url_prefix='/users')
        app.register_blueprint(company_blueprint, url_prefix='/companies')
        app.register_blueprint(workshop_blueprint, url_prefix='/workshops')
        # Create all tables
        db.create_all()

    return app

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))