from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError
from app.models import User
from app.db.database import db
from app.forms.user_form import  UserForm, LoginForm

user_bp = Blueprint('user', __name__)
@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('workshop.workshop_list'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(staffno=form.staffno.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('workshop.workshop_list'))
        flash('Invalid username or password', 'danger')
    return render_template('user/login.html', form=form)

@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('workshop.workshop_list'))
@user_bp.route('/', methods=['GET'])
def user_list():
    # Fetch user data from the database
    form = UserForm()
    users = User.query.all()
    return render_template('user/list.html', users=users, form=form)

@user_bp.route('/user/add', methods=['GET', 'POST'])
def add_user():
    form = UserForm()
    if request.method == 'POST' and form.validate_on_submit():
        try:
            # Add user to the database
            new_user = User(
                staffno=form.staffno.data,
                staffname=form.staffname.data,
                isadmin=form.isadmin.data,
                password_hash=User.set_password(password=form.password.data)
            )
            db.session.add(new_user)
            db.session.commit()
            flash('User has been added successfully.', 'success')
            return redirect(url_for('user.user_list'))
        except IntegrityError:
            db.session.rollback()
            flash('Database error: User could not be added. Please check the form for errors.', 'danger')
            return redirect(url_for('user.user_list'))
    return render_template('user/register.html', form=form)

@user_bp.route('/user/edit/<int:staffno>', methods=['POST'])
def update_user(staffno):
    user = User.query.get_or_404(staffno)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        # Update user in the database
        user.staffname = form.staffname.data
        user.isadmin = form.isadmin.data
        if form.password.data:
            user.password_hash = User.set_password(password=form.password.data)
        db.session.commit()
        flash('User has been updated successfully.', 'success')
        return redirect(url_for('user.user_list'))
    else:
        flash('Failed to update user. Please check the form for errors.', 'danger')
    return redirect(url_for('user.update_user',user=user))


@user_bp.route('/user/delete/<int:staffno>', methods=['POST'])
def delete_user(staffno):
    # Delete user from the database
    user = User.query.get_or_404(staffno)
    db.session.delete(user)
    db.session.commit()
    flash('User has been deleted successfully.', 'success')
    return redirect(url_for('user.user_list'))
@user_bp.route('/user/edit/<int:staffno>', methods=['GET', 'POST'])
def user_edit(staffno):
    user = User.query.get_or_404(staffno)
    form = UserForm(obj=user)
    
    if request.method == 'GET':
        # Don't fill in the password field for GET requests
        form.password.data = ''
    
    if form.validate_on_submit():
        user.staffname = form.staffname.data
        if form.password.data:  # Only update password if provided
            user.set_password(form.password.data)
        user.isadmin = form.isadmin.data
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('user_list',user=user))
    
    return render_template('user/edit.html', form=form, title='Edit User')

@user_bp.route('/users/<int:staffno>/profile')
@login_required
def user_profile(staffno):
    user = User.query.get_or_404(staffno)
    # Only admins can view any profile, regular users can only view their own
    if not current_user.isadmin and current_user.staffno != staffno:
        flash('You do not have permission to view this profile', 'danger')
        return redirect(url_for('workshop.workshop_list'))
    
    return render_template('user/profile.html', user=user) 