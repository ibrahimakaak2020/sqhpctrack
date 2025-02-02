from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Equipment, MaintenanceRecord, MaintenanceStatus, User
from app import db

equipment_bp = Blueprint('equipment', __name__, url_prefix='/equipment')

@equipment_bp.route('/')
def equipment_master():
    equipments = Equipment.query.all()
    return render_template('equipment/equipment_master.html', equipments=equipments)

@equipment_bp.route('/add', methods=['POST'])
def add_equipment():
    if request.method == 'POST':
        sn = request.form['sn']
        model_name = request.form['model_name']
        equipment_type = request.form['equipment_type']
        manufacturer = request.form['manufacturer']
        locname = request.form['locname']
        building = request.form['building']
        note = request.form['note']
        created_by = request.form['created_by']

        new_equipment = Equipment(
            sn=sn, model_name=model_name, equipment_type=equipment_type,
            manufacturer=manufacturer, locname=locname, building=building,
            note=note, created_by=created_by
        )
        db.session.add(new_equipment)
        db.session.commit()
        flash('Equipment added successfully!', 'success')
    return redirect(url_for('equipment.equipment_master'))

@equipment_bp.route('/update/<string:sn>', methods=['POST'])
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
def delete_equipment(sn):
    equipment = Equipment.query.get_or_404(sn)
    db.session.delete(equipment)
    db.session.commit()
    flash('Equipment deleted successfully!', 'success')
    return redirect(url_for('equipment.equipment_master'))