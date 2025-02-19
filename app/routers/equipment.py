import datetime
from time import localtime
from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField, SubmitField, TextAreaField
from app.forms.equipmentforms import AddEquipmentForm, AddMaintenanceForm
from app.forms.maintenancerecordform import MaintenanceRecordForm
from app.forms.maintenancestatus import MaintenanceStatusForm
from app.models import CompanyUser, Equipment, MaintenanceRecord, MaintenanceStatus, User, Workshop, get_equipment_with_pending_status
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
    workshops=Workshop.query.all()
    equipments = Equipment.query.all()
    return render_template('equipment/equipmentmaster.html', equipments=equipments,workshops=workshops, form=form)

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
    try:
        equipment = Equipment.query.get_or_404(sn)
        
        # First, get all maintenance records for this equipment
        maintenance_records = MaintenanceRecord.query.filter_by(equipment_sn=sn).all()
        
        # Delete all associated status updates and maintenance records
        for record in maintenance_records:
            # Delete status updates for this maintenance record
            MaintenanceStatus.query.filter_by(maintenance_id=record.id).delete()
            # Delete the maintenance record
            db.session.delete(record)
        
        # Now delete the equipment
        db.session.delete(equipment)
        db.session.commit()
        
        flash('Equipment and all associated records deleted successfully!', 'success')
        logger.info(f'Equipment {sn} deleted by user {current_user.staffno}')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error deleting equipment {sn}: {str(e)}')
        flash(f'Error deleting equipment: {str(e)}', 'danger')
    
    return redirect(url_for('equipment.equipment_master'))


@equipment_bp.route('/<string:sn>')
def read(sn):
    equipment = Equipment.query.get_or_404(sn)
   
    maintenance= MaintenanceRecord.query.filter_by(equipment_sn=sn).order_by(MaintenanceRecord.maintenance_date.desc()).all()
   
    form=MaintenanceRecordForm()
    formstatus=MaintenanceStatusForm()
    return render_template('equipment/detail.html',
                         equipment=equipment,maintenance=maintenance,
                         current_datetime=localtime,
                          
                         current_user=current_user,get_user_name=User.get_user_name,form=form,formstatus=formstatus)




# Constants
status_colors = {
    'pending': 'secondary',
    'received': 'info',
    'send': 'warning',
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

@equipment_bp.route('/updatestatus/<int:id>', methods=['POST'])
@login_required
def update_status(id):
    record = MaintenanceRecord.query.get_or_404(id)
    formstatus = MaintenanceStatusForm()
    
    if formstatus.validate_on_submit():
        try:
            # Create new status update
            status_update = MaintenanceStatus(
                maintenance_id=record.id,
                status=formstatus.status.data,
                notes=formstatus.notes.data,
                registered_by=current_user.staffno
            )
            
            # Update the main record relationships
            if formstatus.status.data =='sended':
                company = CompanyUser.query.get(formstatus.company_id.data)
                if company:
                    status_update.company_id = company.cid
                    status_update.is_external = True
            else:
                workshop = Workshop.query.get(formstatus.workshop_id.data)
                if workshop:
                    status_update.workshop_id = workshop.id
                    status_update.is_external = False
                    
            if formstatus.status.data == 'closed':
                record.isactive = False
            if formstatus.status.data == 'cancelled':
                record.isactive = False
            
            # Save changes
            db.session.add(status_update)
            db.session.commit()
            
            flash('Status updated successfully', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating status: {str(e)}', 'danger')
            
        return redirect(url_for('equipment.read', sn=record.equipment_sn))
        
    flash('Invalid form submission', 'danger')
    return redirect(url_for('equipment.read', sn=record.equipment_sn))

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
        
            # Create initial status
            initial_status = MaintenanceStatus(maintenance_id=record.id,status='rescheduled',notes='Maintenance request registered',registered_by=current_user.staffno)
            db.session.add(initial_status)
            
            db.session.commit()
            flash('New maintenance record created successfully', 'success')
            return redirect(url_for('equipment.read', sn=sn))
            
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

# Active Maintenance Records
@equipment_bp.route('/active')
@login_required
def active_records():
    active_maintenance = MaintenanceRecord.query.filter(
        MaintenanceRecord.current_status.in_(['pending', 'received', 'in_progress','completed','sending'])
    ).order_by(MaintenanceRecord.maintenance_date.desc()).all()
    return render_template('equipment/active_records.html', records=active_maintenance)

@equipment_bp.route('/pending')
@login_required
def pending_maintenance():
    # Get equipment with pending maintenance
    pending_equipment = get_equipment_with_pending_status()
    formstatus=MaintenanceStatusForm()
    # Or get pending maintenance records
    pending_records = MaintenanceRecord.get_pending_records()
    
    return render_template(
        'equipment/pending_list.html',
        equipment_list=pending_equipment,
        maintenance_records=pending_equipment,formstatus=formstatus
    )
