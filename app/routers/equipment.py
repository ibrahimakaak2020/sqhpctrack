# app/routes/equipment.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime

from flask_login import current_user
from app.models import Equipment
from app import db
from app.utils.localtime import local_time as localtime
equipment_bp = Blueprint('equipment', __name__, url_prefix='/equipment')

@equipment_bp.route('/')
def list():
    equipments = Equipment.query.all()
    return render_template('equipmentmaintenance/list.html', 
                         equipments=equipments,
                         current_datetime=localtime,
                         current_user=current_user)

@equipment_bp.route('/<int:id>')
def detail(id):
    equipment = Equipment.query.get_or_404(id)
    return render_template('equipmentmaintenance/detail.html', 
                         equipment=equipment,
                         current_datetime=localtime,
                         current_user=current_user)

@equipment_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        equipment = Equipment(
            name=request.form['name'],
            serial_number=request.form['serial_number'],
            description=request.form['description']
        )
        db.session.add(equipment)
        db.session.commit()
        flash('Equipment created successfully', 'success')
        return redirect(url_for('equipment.list'))
    
    return render_template('equipmentmaintenance/create.html',
                         current_datetime=localtime,
                         current_user=current_user)