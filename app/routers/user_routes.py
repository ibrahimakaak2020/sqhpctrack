from flask import Blueprint, render_template, flash, redirect, url_for, request
from sqlalchemy.exc import IntegrityError
from app.models import User
from app.db.database import db
from app.forms.user_form import  UserForm

user_bp = Blueprint('user', __name__)

@user_bp.route('/', methods=['GET'])
def user_list():
    # Fetch user data from the database
    form = UserForm()
    users = User.query.all()
    return render_template('user/user_list.html', users=users, form=form)

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
    return render_template('user/user_form.html', form=form)

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
    else:
        flash('Failed to update user. Please check the form for errors.', 'danger')
    return redirect(url_for('user.user_list'))

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
        return redirect(url_for('user_list'))
    
    return render_template('user/user_form.html', form=form, title='Edit User')