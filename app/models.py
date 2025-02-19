from datetime import datetime, timezone
from flask_login import UserMixin
import pytz
from app.db.database import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import event, ForeignKey
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
def get_muscat_time():
    """Returns current time in Muscat timezone"""
    muscat_tz = pytz.timezone('Asia/Muscat')
    utc_now = datetime.now(timezone.utc)
    return utc_now.astimezone(muscat_tz)
class User(db.Model, UserMixin):
    __tablename__ = "user"
    staffno = db.Column( db.String(80), unique=True, nullable=False, primary_key=True, index=True)
    staffname = db.Column(db.String(80), nullable=False)
    isadmin = db.Column(db.Boolean, default=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=get_muscat_time)
    updated_at = db.Column(db.DateTime, default=get_muscat_time, onupdate=get_muscat_time)

    def get_id(self):
        return str(self.staffno)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    @staticmethod
    def get_user_name(staffno):
        user = User.query.filter_by(staffno=staffno).first()
        return user.staffname if user else 'Unknown User'
    # Define the relationship
    registered_maintenance = relationship('MaintenanceRecord', back_populates='user')
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

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
    created_at = db.Column(db.DateTime, default=get_muscat_time)
    created_by = db.Column(db.String(80), db.ForeignKey('user.staffno'), nullable=False)
    def __repr__(self):
        """
        Returns a string representation of the Equipment object.

        The string representation includes the model name and serial number of the equipment.

        Parameters:
        None

        Returns:
        str: A string representation of the Equipment object in the format '<Equipment {model_name} (SN: {sn})>'.
        """
        return f'<Equipment {self.model_name} (SN: {self.sn})>'
        # Relationships
    creator = db.relationship('User', backref=db.backref('created_equipment', lazy=True))
    maintenance_records = db.relationship('MaintenanceRecord', back_populates='equipment_rel', overlaps='equipment_ref')

    def __repr__(self):
            return f'<Equipment {self.model_name} (SN: {self.sn})>'
    def get_active_maintenance(self):
            """
            Returns the active maintenance record for this equipment, if any.
            An active maintenance record is one where the status is 'in_progress'.
            """
            return MaintenanceRecord.query.filter_by(
                equipment_sn=self.sn,
                isactive=True
            ).first()

    @staticmethod
    def get_pending_maintenance():
        """
        Returns all equipment with active maintenance records where the latest status is pending.
        """
        return Equipment.query.join(
            MaintenanceRecord,
            Equipment.sn == MaintenanceRecord.equipment_sn
        ).join(
            MaintenanceStatus,
            MaintenanceStatus.maintenance_id == MaintenanceRecord.id
        ).filter(
            MaintenanceRecord.isactive == True,
            MaintenanceStatus.id.in_(
                db.session.query(
                    db.func.max(MaintenanceStatus.id)
                ).group_by(
                    MaintenanceStatus.maintenance_id
                )
            ),
            MaintenanceStatus.status == 'pending'
        ).order_by(
            MaintenanceStatus.status_date.desc()
        ).all()
        
    from sqlalchemy.orm import aliased
    @staticmethod
    def get_equipment_with_pending():
        # Alias for the MaintenanceStatus table to get the latest status
        latest_status_subquery = db.session.query(
            MaintenanceStatus.maintenance_id,
            db.func.max(MaintenanceStatus.id).label('latest_status_id')
        ).group_by(MaintenanceStatus.maintenance_id).subquery()
        print(latest_status_subquery)
        print('----------------------------------------------------------------')

        # Join Equipment -> MaintenanceRecord -> MaintenanceStatus (using subquery to get the latest status)
        equipment_with_pending_status = db.session.query(Equipment).join(
            MaintenanceRecord, MaintenanceRecord.equipment_sn == Equipment.sn
        ).join(
            latest_status_subquery, latest_status_subquery.c.maintenance_id == MaintenanceRecord.id
        ).join(
            MaintenanceStatus, MaintenanceStatus.id == latest_status_subquery.c.latest_status_id
        ).filter(
            MaintenanceRecord.isactive == True,  # Maintenance is active
            MaintenanceStatus.status == 'pending'  # Last status is 'pending'
        ).all()

        return equipment_with_pending_status


    def has_pending_maintenance(self):
        """
        Checks if equipment has an active maintenance record with pending status.
        """
        latest_maintenance = self.maintenance_records.filter(
            MaintenanceRecord.isactive == True
        ).first()
        
        if latest_maintenance:
            latest_status = latest_maintenance.status_updates.order_by(
                MaintenanceStatus.status_date.desc()
            ).first()
            return latest_status.status == 'pending' if latest_status else True
        
        return False

class MaintenanceRecord(db.Model):
    __tablename__ = "maintenance_record"

    id = db.Column(db.Integer, primary_key=True)
    equipment_sn = db.Column(db.String(50), db.ForeignKey('equipment.sn'), nullable=False)
    
    registered_by = db.Column(db.Integer, db.ForeignKey('user.staffno'), nullable=False)
    maintenance_date = db.Column(db.DateTime, default=get_muscat_time)
    isactive = db.Column(db.Boolean, default=True)
    problem_description = db.Column(db.Text, nullable=False)

    # Relationships
    equipment_rel = db.relationship('Equipment', back_populates='maintenance_records', overlaps='equipment_ref')
    user = relationship('User', back_populates='registered_maintenance')
    
    def __repr__(self):
        return f'<MaintenanceRecord {self.id}>'

    @property
    def latest_status(self):
        latest_status = MaintenanceStatus.query.filter_by(maintenance_id=self.id).order_by(MaintenanceStatus.status_date.desc()).first()
        if latest_status:
            print(f"Latest status for MaintenanceRecord {self.id}: {latest_status.status} on {latest_status.status_date}")
            return latest_status.status
        else:
            print(f"No status updates found for MaintenanceRecord {self.id}")
            return None

    def set_active(self):
        self.isactive = True
        db.session.commit()

    def set_closed(self):
        self.isactive = False
        db.session.commit()

    @property
    def current_status(self):
        """
        Returns the current status of the maintenance record.
        """
        latest = MaintenanceStatus.query.filter_by(
            maintenance_id=self.id
        ).order_by(
            MaintenanceStatus.status_date.desc()
        ).first()
        return latest.status if latest else 'pending'

    @staticmethod
    def get_pending_records():
        """
        Returns all active maintenance records with pending status.
        """
        return MaintenanceRecord.query.join(
            MaintenanceStatus,
            MaintenanceStatus.maintenance_id == MaintenanceRecord.id
        ).filter(
            MaintenanceRecord.isactive == True,
            MaintenanceStatus.status == 'pending'
        ).order_by(
            MaintenanceStatus.status_date.desc()
        ).all()

class MaintenanceStatus(db.Model):
    __tablename__ = 'maintenance_status'

    id = db.Column(db.Integer, primary_key=True)
    maintenance_id = db.Column(db.Integer, db.ForeignKey('maintenance_record.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companyuser.cid'))
    workshop_id = db.Column(db.Integer, db.ForeignKey('workshop.id'))
    status_date = db.Column(db.DateTime, default=get_muscat_time)
    status = db.Column(db.String(20), nullable=False)
    is_external = db.Column(db.Boolean, nullable=False, default=False)
    notes = db.Column(db.Text)
    registered_by = db.Column(db.Integer, db.ForeignKey('user.staffno'), nullable=False)

    # Relationships
    maintenance_record = db.relationship(
        'MaintenanceRecord',
        backref=db.backref('status_updates', lazy='dynamic', cascade='all, delete-orphan')
    )
    workshop = db.relationship(
        'Workshop',
        backref=db.backref('status_updates', lazy='dynamic')
    )
    company = db.relationship(
        'CompanyUser',
        backref=db.backref('status_updates', lazy='dynamic')
    )
    user = db.relationship(
        'User',
        backref=db.backref('registered_status_updates', lazy='dynamic')
    )

    def __repr__(self):
        return f'<MaintenanceStatus {self.id} ({self.status})>'

    def set_maintenance_inactive(self):
        if self.status.lower() == "completed":
            maintenance_record = MaintenanceRecord.query.get(self.maintenance_id)
            if maintenance_record:
                maintenance_record.isactive = False
                db.session.commit()

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
#event.listen(User, 'before_update', update_user_timestamp)
#event.listen(Equipment, 'before_insert', log_equipment_creation)
#event.listen(MaintenanceRecord, 'before_insert', check_active_maintenance)
#event.listen(MaintenanceStatus, 'before_insert', set_maintenance_inactive)

def get_equipment_with_pending_status():
    # Alias for the MaintenanceStatus table to get the latest status
    latest_status_subquery = db.session.query(
        MaintenanceStatus.maintenance_id,
        db.func.max(MaintenanceStatus.id).label('latest_status_id')
    ).group_by(MaintenanceStatus.maintenance_id).subquery()

    # Query Equipment -> MaintenanceRecord -> Latest MaintenanceStatus
    equipment_with_pending_status = db.session.query(Equipment).join(
        MaintenanceRecord, MaintenanceRecord.equipment_sn == Equipment.sn
    ).join(
        latest_status_subquery, latest_status_subquery.c.maintenance_id == MaintenanceRecord.id
    ).join(
        MaintenanceStatus, MaintenanceStatus.id == latest_status_subquery.c.latest_status_id
    ).filter(
        MaintenanceRecord.isactive == True,  # Active maintenance
        MaintenanceStatus.status == 'pending'  # Latest status is 'pending'
    ).all()

    return equipment_with_pending_status