from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user

from app.models import User
from app.forms.user_forms import LoginForm, RegistrationForm, UserUpdateForm
from app import db
from app.utils.decorators import admin_required
import logging

logger = logging.getLogger(__name__)
users_bp = Blueprint('users', __name__)

@users_bp.route('/login', methods=['GET', 'POST'])

def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if request.method == 'POST':
        try:
            # Print form data for debugging
            logger.debug(f"Form Data: {request.form}")
            logger.debug(f"CSRF Token: {request.form.get('csrf_token')}")
            
            if form.validate_on_submit():
                user = User.query.filter_by(staffno=form.staffno.data).first()
                if user and user.check_password(form.password.data):
                    session.permanent = True
                    login_user(user, remember=form.remember_me.data)
                    logger.info(f'User {user.staffno} logged in successfully')
                    
                    next_page = request.args.get('next')
                    if next_page:
                        return redirect(next_page)
                    return redirect(url_for('main.index'))
                
                logger.warning(f'Failed login attempt for staff number: {form.staffno.data}')
                flash('Invalid staff number or password', 'danger')
            else:
                logger.error(f'Form validation errors: {form.errors}')
                for field, errors in form.errors.items():
                    for error in errors:
                        flash(f'{getattr(form, field).label.text}: {error}', 'danger')
                
        except Exception as e:
            logger.error(f'Login error: {str(e)}')
            flash('An error occurred during login. Please try again.', 'danger')
    
    return render_template('users/login.html', form=form)

@users_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@users_bp.route('/register', methods=['GET', 'POST'])
def register():
    # if not current_user.is_authenticated:
    #     return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            staffno=form.staffno.data,
            staffname=form.staffname.data,
            isadmin=form.isadmin.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User has been registered successfully', 'success')
        return redirect(url_for('users.user_list'))
    return render_template('users/register.html', form=form)

@users_bp.route('/users', methods=['GET'])
@login_required
def user_list():
    form = LoginForm()
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    query = User.query

    if search:
        query = query.filter((User.staffno.like(f'%{search}%')) | (User.staffname.like(f'%{search}%')))

    users = query.paginate(page=page, per_page=10)
    return render_template('users/list.html', users=users, search=search,form=form)

@users_bp.route('/users/<int:staffno>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(staffno):
    if not current_user.isadmin and current_user.staffno == staffno:
        flash('You do not have permission to edit this user', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(staffno)
    form = UserUpdateForm(obj=user)
    
    if form.validate_on_submit():
        user.staffname = form.staffname.data
        if form.password.data:
            user.set_password(form.password.data)
        if current_user.isadmin:
            user.isadmin = form.isadmin.data
        db.session.commit()
        flash('User has been updated successfully', 'success')
        return redirect(url_for('users.user_list'))
    return render_template('users/edit.html', form=form, user=user)

@users_bp.route('/users/<int:staffno>/delete', methods=['POST'])
@login_required
def delete_user(staffno):
    if not current_user.isadmin:
        flash('Only administrators can delete users', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(staffno)
    if user.staffno == current_user.staffno:
        flash('You cannot delete your own account', 'danger')
        return redirect(url_for('users.user_list'))
    
    db.session.delete(user)
    db.session.commit()
    flash('User has been deleted successfully', 'success')
    return redirect(url_for('users.user_list'))

@users_bp.route('/users/<int:staffno>/profile')
@login_required
def user_profile(staffno):
    user = User.query.get_or_404(staffno)
    # Only admins can view any profile, regular users can only view their own
    if not current_user.isadmin and current_user.staffno == staffno:
        flash('You do not have permission to view this profile', 'danger')
        return redirect(url_for('main.index'))
    
    return render_template('users/profile.html', user=user)