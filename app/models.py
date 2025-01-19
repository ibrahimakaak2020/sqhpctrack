from datetime import datetime, timezone
from flask_login import UserMixin
from app.db.database import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError

class User(db.Model, UserMixin):
    __tablename__ = "user"

    staffno = db.Column(db.Integer, primary_key=True, index=True)
    staffname = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(128))
    isadmin = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def get_id(self):
        return str(self.staffno)

   
    def set_password(cls, password):
        return generate_password_hash(password)

   
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class CompanyUser(db.Model):
    __tablename__ = "companyuser"

    cid = db.Column(db.Integer, primary_key=True, index=True)
    staffname = db.Column(db.String(100), nullable=False)
    companyname_en = db.Column(db.String(100), nullable=False)
    companyname_ar = db.Column(db.String(100), nullable=False)
    contactnumber = db.Column(db.String(30), nullable=False, index=True)

class Workshop(db.Model):
    __tablename__ = "workshop"

    id = db.Column(db.Integer, primary_key=True)
    workshopname = db.Column(db.String(100), nullable=False)
    building = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100))

class Equipment(db.Model):
    __tablename__ = "equipment"

    sn = db.Column(db.String(50), primary_key=True, index=True)
    model_name = db.Column(db.String(100), nullable=False)
    equipment_type = db.Column(db.String(50), nullable=False)
    manufacturer = db.Column(db.String(100), nullable=False)
    locname = db.Column(db.String(100), nullable=False)
    building = db.Column(db.String(100), nullable=False)
    note = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    created_by = db.Column(db.Integer, db.ForeignKey('user.staffno'), nullable=False)

    # Relationships
    creator = db.relationship('User', backref=db.backref('created_equipment', lazy=True))

    def __repr__(self):
        return f'<Equipment {self.model_name} (SN: {self.sn})>'

class MaintenanceRecord(db.Model):
    __tablename__ = "maintenance_record"

    id = db.Column(db.Integer, primary_key=True)
    equipment_sn = db.Column(db.String(50), db.ForeignKey('equipment.sn'), nullable=False)
    registered_by = db.Column(db.Integer, db.ForeignKey('user.staffno'), nullable=False)
    maintenance_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    isactive = db.Column(db.Boolean, default=True)
    problem_description = db.Column(db.Text, nullable=False)

    # Relationships
    equipment = db.relationship('Equipment', backref=db.backref('maintenance_records', lazy=True))
    registrar = db.relationship('User', backref=db.backref('registered_maintenance', lazy=True))
    
    def __repr__(self):
        return f'<MaintenanceRecord {self.id}>'

    @property
    def latest_status(self):
        return self.status_updates.order_by(MaintenanceStatus.status_date.desc()).first()

class MaintenanceStatus(db.Model):
    __tablename__ = "maintenance_status"

    id = db.Column(db.Integer, primary_key=True)
    maintenance_id = db.Column(db.Integer, db.ForeignKey('maintenance_record.id'), nullable=False)
    workshop_id = db.Column(db.Integer, db.ForeignKey('workshop.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('companyuser.cid'))
    status_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    status = db.Column(db.String(20), nullable=False)
    is_external = db.Column(db.Boolean, nullable=False)
    notes = db.Column(db.Text)
    register_by = db.Column(db.Integer, db.ForeignKey('user.staffno'), nullable=False)

    # Relationships
    maintenance = db.relationship('MaintenanceRecord', backref=db.backref('status_updates', lazy=True))
    workshop = db.relationship('Workshop', backref=db.backref('status_updates', lazy=True))
    company = db.relationship('CompanyUser', backref=db.backref('status_updates', lazy=True))
    registrar = db.relationship('User', backref=db.backref('registered_status_updates', lazy=True))

    def __repr__(self):
        return f'<MaintenanceStatus {self.id} ({self.status})>'

# Event handlers
def update_user_timestamp(mapper, connection, target):
    target.updated_at = datetime.now(timezone.utc)

def log_equipment_creation(mapper, connection, target):
    print(f"Equipment {target.model_name} with SN {target.sn} is being created")

def check_active_maintenance(mapper, connection, target):
    active_maintenance = MaintenanceRecord.query.filter_by(equipment_sn=target.equipment_sn, isactive=True).first()
    if active_maintenance:
        raise IntegrityError("Active maintenance record exists for this equipment.", params=None, orig=None)

def set_maintenance_inactive(mapper, connection, target):
    if target.status.lower() == "completed":
        maintenance_record = MaintenanceRecord.query.get(target.maintenance_id)
        if maintenance_record:
            maintenance_record.isactive = False
            db.session.add(maintenance_record)
            db.session.commit()

# Register event listeners
event.listen(User, 'before_update', update_user_timestamp)
event.listen(Equipment, 'before_insert', log_equipment_creation)
event.listen(MaintenanceRecord, 'before_insert', check_active_maintenance)
event.listen(MaintenanceStatus, 'before_insert', set_maintenance_inactive)