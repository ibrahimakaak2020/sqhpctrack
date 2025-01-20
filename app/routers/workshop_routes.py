from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Workshop
from app.forms.workshop_forms import WorkshopUserForm, WorkshopSearchForm
from app.db.database import db


workshop_bp = Blueprint('workshop', __name__)

@workshop_bp.route('/workshops')
@login_required
def workshop_list():
    search = request.args.get('search', '')
    query = Workshop.query
    
    if search:
        query = query.filter(
            db.or_(
                Workshop.workshopname.ilike(f'%{search}%'),
                Workshop.building.ilike(f'%{search}%'),
                Workshop.contact.ilike(f'%{search}%'),
                
            )
        )
    
    workshops = query.order_by(Workshop.workshopname).all()
    search_form = WorkshopSearchForm()
    search_form.search.data = search
    
    return render_template('workshop/list.html', 
                         workshops=workshops, 
                         search_form=search_form)

@workshop_bp.route('/workshops/add', methods=['GET', 'POST'])
@login_required

def add_workshop():
    form = WorkshopUserForm()
    if form.validate_on_submit():
        workshop = Workshop(
            workshopname=form.workshopname.data,
            building=form.building.data,
            contact=form.contact.data
        )
        db.session.add(workshop)
        try:
            db.session.commit()
            flash('Workshop added successfully', 'success')
            return redirect(url_for('workshop.workshop_list'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the workshop. Please try again.', 'danger')
    
    return render_template('workshop/form.html', form=form, title='Add New Workshop')

@workshop_bp.route('/workshops/<int:id>/edit', methods=['GET', 'POST'])
@login_required

def edit_workshop(id):
    workshop = Workshop.query.get_or_404(id)
    form = WorkshopUserForm(obj=workshop)
    
    if form.validate_on_submit():
        if workshop.workshopname != form.workshopname.data:
                workshop.workshopname = form.workshopname.data
        if workshop.building != form.building.data:
            workshop.building = form.building.data
        if workshop.contact != form.contact.data:
            workshop.contact = form.contact.data
      
        db.session.commit()
        flash('Workshop updated successfully', 'success')
        return redirect(url_for('workshop.workshop_list'))
    
    return render_template('workshop/form.html', form=form, company=workshop, title='Edit Workshop')

@workshop_bp.route('/workshops/<int:id>/delete', methods=['POST'])
@login_required

def delete_workshop(id):
    workshop = Workshop.query.get_or_404(id)
    db.session.delete(workshop)
    db.session.commit()
    flash('Workshop deleted successfully', 'success')
    return redirect(url_for('workshop.workshop_list')) 