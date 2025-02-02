from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    staff_number = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    maintenance_records = db.relationship('MaintenanceRecord', backref='registered_by', lazy=True)
    statuses = db.relationship('MaintenanceStatus', backref='registered_by', lazy=True)

class Equipment(db.Model):
    __tablename__ = 'equipment'
    serial_number = db.Column(db.String(50), primary_key=True)
    model_name = db.Column(db.String(100), nullable=False)
    equipment_type = db.Column(db.String(50), nullable=False)
    manufacturer = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    building = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(20), db.ForeignKey('users.staff_number'), nullable=False)
    
    # Relationships
    maintenance_records = db.relationship('MaintenanceRecord', backref='equipment', lazy=True)

class MaintenanceRecord(db.Model):
    __tablename__ = 'maintenance_records'
    id = db.Column(db.Integer, primary_key=True)
    equipment_sn = db.Column(db.String(50), db.ForeignKey('equipment.serial_number'), nullable=False)
    maintenance_id = db.Column(db.String(50), unique=True, nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    problem_description = db.Column(db.Text, nullable=False)
    registered_by_staff_number = db.Column(db.String(20), db.ForeignKey('users.staff_number'), nullable=False)
    
    # Relationships
    statuses = db.relationship('MaintenanceStatus', backref='maintenance_record', lazy=True)

class MaintenanceStatus(db.Model):
    __tablename__ = 'maintenance_status'
    id = db.Column(db.Integer, primary_key=True)
    maintenance_id = db.Column(db.Integer, db.ForeignKey('maintenance_records.id'), nullable=False)
    status_date = db.Column(db.DateTime, default=datetime.utcnow)
    status_type = db.Column(db.String(20), nullable=False)  # Open, In Progress, Completed
    notes = db.Column(db.Text, nullable=True)
    registered_by_staff_number = db.Column(db.String(20), db.ForeignKey('users.staff_number'), nullable=False)

    def deactivate_maintenance(self):
        if self.status_type == "Completed":
            maintenance_record = MaintenanceRecord.query.get(self.maintenance_id)
            if maintenance_record:
                maintenance_record.active = False
                db.session.commit()