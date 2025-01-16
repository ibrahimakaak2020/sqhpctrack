from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

from app.config.config import config_dict

from  app.db.database import db,init_db,login_manager

def create_app(config_name='default'):
    app = Flask(__name__)
  
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

    
    with app.app_context():
        # Import models to ensure tables are created
        from .models import User, CompanyUser, Workshop, Equipment, MaintenanceRecord, MaintenanceStatus
        
        from .routers.user_routes import user_bp as user_blueprint
        #from .main.routes import main as main_blueprint
        #from .companyuser import companyuser as companyuser_blueprint
        #from .workshop import workshop as workshop_blueprint
        #from .equipment import equipment as equipment_blueprint
        #from .maintenancerecord import maintenancerecord as maintenancerecord_blueprint
        #from .maintenancestatus import maintenancestatus as maintenancestatus_blueprint

        app.register_blueprint(user_blueprint, url_prefix='/users')
        #app.register_blueprint(main_blueprint, url_prefix='/main')
        #app.register_blueprint(companyuser_blueprint, url_prefix='/companyusers')
        #app.register_blueprint(workshop_blueprint, url_prefix='/workshops')
        #app.register_blueprint(equipment_blueprint, url_prefix='/equipment')
        #app.register_blueprint(maintenancerecord_blueprint, url_prefix='/maintenancerecords')
        #app.register_blueprint(maintenancestatus_blueprint, url_prefix='/maintenancestatuses')
        
        # Create all tables
        db.create_all()

    return app

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))