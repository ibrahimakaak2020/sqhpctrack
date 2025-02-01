from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from flask_login import current_user
from app.models import Equipment
from app import db
from app.utils.localtime import local_time as localtime

equipment_bp = Blueprint('equipment', __name__)

@equipment_bp.route('/')
def list():
    equipments = Equipment.query.all()
    return render_template('equipmentmaintenance/index.html', 
                         equipments=equipments,
                         current_datetime=localtime,
                         current_user=current_user)

@equipment_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        try:
            sn = request.form['sn']
            model_name = request.form['model_name']
            equipment_type = request.form['equipment_type']
            manufacturer = request.form['manufacturer']
            locname = request.form['locname']
            building = request.form['building']
            note = request.form.get('note', '')

            equipment = Equipment(
                sn=sn,
                model_name=model_name,
                equipment_type=equipment_type,
                manufacturer=manufacturer,
                locname=locname,
                building=building,
                note=note,
                created_by=current_user.staffno
            )

            db.session.add(equipment)
            db.session.commit()
            flash('Equipment created successfully', 'success')
            return redirect(url_for('equipment.list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating equipment: {str(e)}', 'error')
    
    return render_template('equipmentmaintenance/create.html',
                         current_datetime=localtime,
                         current_user=current_user)

@equipment_bp.route('/<string:sn>')
def read(sn):
    equipment = Equipment.query.get_or_404(sn)
    return render_template('equipmentmaintenance/read.html',
                         equipment=equipment,
                         current_datetime=localtime,
                         current_user=current_user)

@equipment_bp.route('/<string:sn>/update', methods=['GET', 'POST'])
def update(sn):
    equipment = Equipment.query.get_or_404(sn)
    
    if request.method == 'POST':
        try:
            equipment.model_name = request.form['model_name']
            equipment.equipment_type = request.form['equipment_type']
            equipment.manufacturer = request.form['manufacturer']
            equipment.locname = request.form['locname']
            equipment.building = request.form['building']
            equipment.note = request.form.get('note', '')

            db.session.commit()
            flash('Equipment updated successfully', 'success')
            return redirect(url_for('equipment.read', sn=sn))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating equipment: {str(e)}', 'error')
    
    return render_template('equipmentmaintenance/update.html',
                         equipment=equipment,
                         current_datetime=localtime,
                         current_user=current_user)

@equipment_bp.route('/<string:sn>/delete', methods=['POST'])
def delete(sn):
    equipment = Equipment.query.get_or_404(sn)
    try:
        db.session.delete(equipment)
        db.session.commit()
        flash('Equipment deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting equipment: {str(e)}', 'error')
    
    return redirect(url_for('equipment.list'))