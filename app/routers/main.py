from flask import Blueprint, render_template,redirect,url_for
from flask_login import login_required, current_user
from app.db.database import db
from app.models import Equipment, MaintenanceRecord, MaintenanceStatus, User
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Add any dashboard statistics or data you want to display
    total_equipment = Equipment.query.count()
    # under_maintenance_count = Equipment.query.all().count()
    active_maintenance_count = MaintenanceRecord.query.filter_by(isactive=True).count()
    # closed_maintenance_count = MaintenanceRecord.query.filter_by(isactive=False).count()

    statuses = db.session.query(MaintenanceStatus.status, db.func.count(MaintenanceStatus.status)).group_by(MaintenanceStatus.status).all()
    
    equipment_by_type = db.session.query(Equipment.equipment_type, db.func.count(Equipment.sn)).group_by(Equipment.equipment_type).all()

    notification_count = 0  # Set this to your actual notification count logic
    stats = {
        'total_users': db.session.query(User).count(),
        'total_equipment':total_equipment,
        'under_maintenance_count':0,
        'active_maintenance_count':active_maintenance_count,
        'closed_maintenance_count':0
        # Add more statistics as needed
    }
    return render_template('main/dashboard.html', stats=stats, notification_count=notification_count) 