import datetime
from time import localtime
from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField, SubmitField, TextAreaField
from app.forms.equipmentforms import AddEquipmentForm, AddMaintenanceForm
from app.forms.maintenancerecordform import MaintenanceRecordForm
from app.forms.maintenancestatus import MaintenanceStatusForm
from app.models import CompanyUser, Equipment, MaintenanceRecord, MaintenanceStatus, User, Workshop
from app import db
from app.utils.decorators import admin_required
from wtforms.validators import DataRequired, Length, Regexp, ValidationError
from sqlalchemy.exc import IntegrityError
from urllib.parse import urlparse


import logging

logger = logging.getLogger(__name__)

equipment_bp = Blueprint('equipment', __name__, url_prefix='/equipment')

@equipment_bp.route('/')
@login_required
def equipment_master():
    form=AddEquipmentForm()
    equipments = Equipment.query.all()
    return render_template('equipment/equipmentmaster.html', equipments=equipments, form=form)

@equipment_bp.route('/add', methods=['POST'])
@login_required
@admin_required
def add_equipment():
    form = AddEquipmentForm()
    if form.validate_on_submit():
        try:
            # Check for existing equipment
            existing_equipment = Equipment.query.filter_by(sn=form.sn.data).first()
            if existing_equipment:
                flash('Equipment with this Serial Number already exists.', 'danger')
                return redirect(url_for('equipment.equipment_master'))
            
            # Create new equipment
            new_equipment = Equipment(
                sn=form.sn.data,
                model_name=form.model_name.data,
                equipment_type=form.equipment_type.data,
                manufacturer=form.manufacturer.data,
                locname=form.locname.data,
                building=form.building.data,
                note=form.note.data,
                created_by=current_user.staffno
            )
            
            db.session.add(new_equipment)
            db.session.commit()
            
            logger.info(f'Equipment {new_equipment.sn} added by user {current_user.staffno}')
            flash('Equipment added successfully!', 'success')
            
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error adding equipment: {str(e)}')
            flash(f'Error adding equipment: {str(e)}', 'danger')
            
        return redirect(url_for('equipment.equipment_master'))
        
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{getattr(form, field).label.text}: {error}', 'danger')
            
    return redirect(url_for('equipment.equipment_master'))

@equipment_bp.route('/update/<string:sn>', methods=['POST'])
@login_required
@admin_required
def update_equipment(sn):
    equipment = Equipment.query.get_or_404(sn)
    if request.method == 'POST':
        equipment.model_name = request.form['model_name']
        equipment.equipment_type = request.form['equipment_type']
        equipment.manufacturer = request.form['manufacturer']
        equipment.locname = request.form['locname']
        equipment.building = request.form['building']
        equipment.note = request.form['note']
        db.session.commit()
        flash('Equipment updated successfully!', 'success')
    return redirect(url_for('equipment.equipment_master'))

@equipment_bp.route('/delete/<string:sn>', methods=['POST'])
@login_required
@admin_required
def delete_equipment(sn):
    equipment = Equipment.query.get_or_404(sn)
    db.session.delete(equipment)
    db.session.commit()
    flash('Equipment deleted successfully!', 'success')
    return redirect(url_for('equipment.equipment_master'))


@equipment_bp.route('/<string:sn>')
def read(sn):
    equipment = Equipment.query.get_or_404(sn)
    form=MaintenanceRecordForm()
    formstatus=MaintenanceStatusForm()
    return render_template('equipment/detail.html',
                         equipment=equipment,
                         current_datetime=localtime,
                         current_user=current_user,get_user_name=User.get_user_name,form=form,formstatus=formstatus)



# Create Blueprint
maintenance = Blueprint('maintenance', __name__, 
                       template_folder='templates',
                       url_prefix='/maintenance')

# Constants
status_colors = {
    'pending': 'secondary',
    'received': 'info',
    'diagnosed': 'warning',
    'in_progress': 'primary',
    'completed': 'success',
    'cancelled': 'danger'
}

# Forms
class StatusUpdateForm(FlaskForm):
    status = SelectField('Status', validators=[DataRequired()],
                        choices=[
                            ('received', 'Mark as Received'),
                            ('diagnosed', 'Mark as Diagnosed'),
                            ('in_progress', 'Start Repair'),
                            ('completed', 'Mark as Completed'),
                            ('cancelled', 'Cancel Maintenance')
                        ])
    notes = TextAreaField('Status Notes', validators=[DataRequired()])
    final_cost = FloatField('Final Cost')
    resolution_notes = TextAreaField('Resolution Notes')
    submit = SubmitField('Update Status')

    def set_status_choices(self, current_status):
        if current_status == 'pending':
            self.status.choices = [('received', 'Mark as Received')]
        elif current_status == 'received':
            self.status.choices = [('diagnosed', 'Mark as Diagnosed')]
        elif current_status == 'diagnosed':
            self.status.choices = [('in_progress', 'Start Repair')]
        elif current_status == 'in_progress':
            self.status.choices = [('completed', 'Mark as Completed')]
        
        # Always allow cancellation
        self.status.choices.append(('cancelled', 'Cancel Maintenance'))

# Context Processors
@equipment_bp.context_processor
def utility_processor():
    return dict(status_colors=status_colors)

# Routes
@equipment_bp.route('/equipment/<string:sn>')
@login_required
def equipment_history(sn):
    equipment = Equipment.query.get_or_404(sn)
    maintenance_records = MaintenanceRecord.query.filter_by(equipment_sn=sn)\
        .order_by(MaintenanceRecord.maintenance_date.desc()).all()
    return render_template('maintenance/history.html', 
                         equipment=equipment, 
                         records=maintenance_records)

@equipment_bp.route('/record/<int:record_id>')
@login_required
def record_detail(record_id):
    record = MaintenanceRecord.query.get_or_404(record_id)
    status_updates = MaintenanceStatus.query\
        .filter_by(maintenance_id=record_id)\
        .order_by(MaintenanceStatus.status_date.desc()).all()
    
    form = StatusUpdateForm()
    form.set_status_choices(record.current_status)
    
    return render_template('maintenance/detail.html',
                         record=record,
                         status_updates=status_updates,
                         form=form)

@equipment_bp.route('/record/<int:record_id>/update-status', methods=['POST'])
@login_required
def update_status(record_id):
    record = MaintenanceRecord.query.get_or_404(record_id)
    form = StatusUpdateForm()
    form.set_status_choices(record.current_status)
    
    if form.validate_on_submit():
        status_update = MaintenanceStatus(
            maintenance_id=record_id,
            status=form.status.data,
            notes=form.notes.data,
            updated_by=current_user.staffno
        )
        
        # Update the main record
        record.current_status = form.status.data
        if form.status.data == 'completed':
            record.completion_date = datetime.now(datetime.timezone.utc)
            record.final_cost = form.final_cost.data
            record.resolution_notes = form.resolution_notes.data
        
        db.session.add(status_update)
        db.session.commit()
        
        flash('Maintenance status updated successfully', 'success')
        return redirect(url_for('maintenance.record_detail', record_id=record_id))
    
    flash('Error updating status', 'error')
    return redirect(url_for('maintenance.record_detail', record_id=record_id))

@equipment_bp.route('/new/<string:sn>', methods=['GET', 'POST'])
@login_required
def new_maintenance(sn):
    equipment = Equipment.query.get_or_404(sn)
    form = AddMaintenanceForm()
    if request.method == 'POST':
        print("*********** from POST")
        try:
           
            record = MaintenanceRecord(
                equipment_sn=sn,
                registered_by=current_user.staffno, 
                problem_description=request.form.get('problem_description')
                
            )
          
            
           
            # Save the maintenance record
            db.session.add(record)
            db.session.commit()
           
            db.session.commit()

            

            
            # Create initial status
            initial_status = MaintenanceStatus(maintenance_id=record.id,status='pending',notes='Maintenance request registered',updated_by=current_user.staffno)
            db.session.add(initial_status)
            
            db.session.commit()
            flash('New maintenance record created successfully', 'success')
            return redirect(url_for('main.dashboard', record_id=record.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating maintenance record: {str(e)}', 'error')
            print(e)
    
  
    return redirect(url_for('equipment.read', sn=sn))

@equipment_bp.route('/record/<int:record_id>/delete', methods=['POST'])
@login_required
def delete_record(record_id):
    record = MaintenanceRecord.query.get_or_404(record_id)
    
    # Check if user has permission to delete
    if not current_user.isadmin and record.registered_by != current_user.staffno:
        flash('You do not have permission to delete this record', 'error')
        return redirect(url_for('maintenance.record_detail', record_id=record_id))
    
    try:
        # Delete associated status updates first
        MaintenanceStatus.query.filter_by(maintenance_id=record_id).delete()
        db.session.delete(record)
        db.session.commit()
        flash('Maintenance record deleted successfully', 'success')
        return redirect(url_for('maintenance.equipment_history', sn=record.equipment_sn))
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting maintenance record: {str(e)}', 'error')
        return redirect(url_for('maintenance.record_detail', record_id=record_id))

# API Routes for AJAX updates
@equipment_bp.route('/api/record/<int:record_id>/status', methods=['GET'])
@login_required
def get_status_history(record_id):
    status_updates = MaintenanceStatus.query\
        .filter_by(maintenance_id=record_id)\
        .order_by(MaintenanceStatus.status_date.desc())\
        .all()
    
    return jsonify([{
        'status': status.status,
        'notes': status.notes,
        'date': status.status_date.isoformat(),
        'updated_by': status.user.staffname
    } for status in status_updates])

# Equipment List Route
@equipment_bp.route('/equipment/<string:sn>')
@login_required
def view_equipment(sn):
    equipment = Equipment.query.all()
    # Get all active maintenance records for each equipment
    maintenance_records = {}
    for eq in equipment:
        maintenance_records[eq.sn] = MaintenanceRecord.query.filter_by(equipment_sn=eq.sn)\
            .filter(MaintenanceRecord.current_status.in_(['pending', 'received', 'diagnosed', 'in_progress']))\
            .order_by(MaintenanceRecord.maintenance_date.desc())\
            .all()
    
    return render_template('maintenance/equipment_list.html', 
                         equipment=equipment,
                         maintenance_records=maintenance_records)

# Active Maintenance Records
@equipment_bp.route('/active')
@login_required
def active_records():
    active_maintenance = MaintenanceRecord.query.filter(
        MaintenanceRecord.current_status.in_(['pending', 'received', 'diagnosed', 'in_progress'])
    ).order_by(MaintenanceRecord.maintenance_date.desc()).all()
    return render_template('equipment/active_records.html', records=active_maintenance)



# Initialize blueprint


@equipment_bp.route('/maintenance/status/add', methods=['GET', 'POST'])
@login_required
def add_maintenance_status():
   
    
    if request.formstatus.validate_on_submit():
        try:
            status = MaintenanceStatus(
                maintenance_id=request.formstatus.maintenance_id.data,
                maintenance_date=request.formstatus.maintenance_date.data,
                workshop_id=request.formstatus.workshop_id.data if not request.formstatus.is_external.data else None,
                company_id=request.formstatus.company_id.data if request.formstatus.is_external.data else None,
                status=request.formstatus.status.data,
                is_external=request.formstatus.is_external.data,
                notes=request.formstatus.notes.data,
                register_by=request.formstatus.register_by.data,
                
            )
            
            db.session.add(status)
            db.session.commit()
            
            flash('Maintenance status added successfully.', 'success')
            return jsonify({'success': True})
            
        except IntegrityError:
            db.session.rollback()
            flash('Error: Status already exists for this maintenance record.', 'danger')
            return jsonify({'success': False, 'error': 'Status already exists'})
        except Exception as e:
            db.session.rollback()
           
            flash('Error adding maintenance status. Please try again.', 'danger')
            return jsonify({'success': False, 'error': 'Unknown error occurred'})
    
    return render_template('maintenance/status_add.html', 
                         title='Add Maintenance Status',
                         status_choices=[('pending', 'Pending'), 
                                       ('in-progress', 'In Progress'), 
                                       ('complete', 'Complete'), 
                                       ('closed', 'Closed')])