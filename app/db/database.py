from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def init_db(app):
    """Initialize database and login manager"""
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Configure Flask-Login
    #login_manager.login_view = 'user.get_users'
    #login_manager.login_message_category = 'info'
    
    # Create tables if they don't exist
    # with app.app_context():
    #     db.create_all()
    #     print("Database tables created")

@login_manager.user_loader
def load_user(user_id):
    from ..models import User
    return User.query.get(int(user_id)) 