import datetime
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, login_user, logout_user
from maintenance_app.models import db, Equipment, MaintenanceRecord, MaintenanceStatus, User
from maintenance_app.forms import LoginForm, EquipmentForm, MaintenanceRecordForm, StatusForm

app = Flask(__name__)
app.config.from_object('config')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(staff_number=form.staff_number.data).first()
        if user and user.password_hash == form.password.data:  # Simple password check (use hashing in production)
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials.", "danger")
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/register_equipment', methods=['GET', 'POST'])
@login_required
def register_equipment():
    if not current_user.is_admin:
        flash("You do not have permission to register equipment.", "danger")
        return redirect(url_for('index'))
    
    form = EquipmentForm()
    if form.validate_on_submit():
        equipment = Equipment(
            serial_number=form.serial_number.data,
            model_name=form.model_name.data,
            equipment_type=form.equipment_type.data,
            manufacturer=form.manufacturer.data,
            location=form.location.data,
            building=form.building.data,
            notes=form.notes.data,
            created_by=current_user.staff_number
        )
        db.session.add(equipment)
        db.session.commit()
        flash("Equipment registered successfully!", "success")
        return redirect(url_for('equipment_overview'))
    
    return render_template('equipment.html', form=form)

@app.route('/create_maintenance_record', methods=['GET', 'POST'])
@login_required
def create_maintenance_record():
    form = MaintenanceRecordForm()
    form.equipment_sn.choices = [(e.serial_number, e.serial_number) for e in Equipment.query.all()]
    
    if form.validate_on_submit():
        equipment = Equipment.query.get(form.equipment_sn.data)
        if equipment:
            # Check if there's already an active maintenance record
            active_record = MaintenanceRecord.query.filter_by(equipment_sn=equipment.serial_number, active=True).first()
            if active_record:
                flash("There is already an active maintenance record for this equipment.", "danger")
                return redirect(url_for('create_maintenance_record'))
            
            maintenance_record = MaintenanceRecord(
                equipment_sn=equipment.serial_number,
                maintenance_id=f"MR-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                problem_description=form.problem_description.data,
                registered_by_staff_number=current_user.staff_number
            )
            db.session.add(maintenance_record)
            db.session.commit()
            flash("Maintenance record created successfully!", "success")
            return redirect(url_for('maintenance_details', record_id=maintenance_record.id))
    
    return render_template('maintenance.html', form=form)

@app.route('/add_status/<int:record_id>', methods=['GET', 'POST'])
@login_required
def add_status(record_id):
    maintenance_record = MaintenanceRecord.query.get_or_404(record_id)
    form = StatusForm()
    
    if form.validate_on_submit():
        status = MaintenanceStatus(
            maintenance_id=maintenance_record.id,
            status_type=form.status_type.data,
            notes=form.notes.data,
            registered_by_staff_number=current_user.staff_number
        )
        db.session.add(status)
        db.session.commit()
        
        # Deactivate maintenance record if status is "Completed"
        if form.status_type.data == "Completed":
            status.deactivate_maintenance()
            flash("Maintenance record marked as completed.", "success")
        
        return redirect(url_for('maintenance_details', record_id=record_id))
    
    return render_template('status.html', form=form, maintenance_record=maintenance_record)

@app.route('/equipment_overview')
@login_required
def equipment_overview():
    equipment_list = Equipment.query.all()
    return render_template('equipment_overview.html', equipment_list=equipment_list)

@app.route('/maintenance_details/<int:record_id>')
@login_required
def maintenance_details(record_id):
    maintenance_record = MaintenanceRecord.query.get_or_404(record_id)
    return render_template('maintenance_details.html', maintenance_record=maintenance_record)