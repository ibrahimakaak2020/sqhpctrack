from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app.forms.user_forms import LoginForm, RegistrationForm, UserUpdateForm
from app import db
from app.utils.decorators import admin_required

users_bp = Blueprint('users', __name__)

@users_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(staffno=form.staffno.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            print('next_page',next_page)
            return redirect(next_page or url_for('main.index'))
        flash('Invalid username or password', 'danger')
    return render_template('users/login.html', form=form)

@users_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@users_bp.route('/register', methods=['GET', 'POST'])
#@login_required
def register():
    # if not current_user.isadmin:
    #     flash('Only administrators can register new users', 'danger')
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

@users_bp.route('/users')
@login_required
@admin_required
def user_list():
    users = User.query.all()
    return render_template('users/list.html', users=users)

@users_bp.route('/users/<int:staffno>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(staffno):
    if not current_user.isadmin and current_user.staffno != staffno:
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
    if not current_user.isadmin and current_user.staffno != staffno:
        flash('You do not have permission to view this profile', 'danger')
        return redirect(url_for('main.index'))
    
    return render_template('users/profile.html', user=user) 