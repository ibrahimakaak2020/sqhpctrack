from flask import Blueprint, render_template, redirect, url_for, request, flash  # Import flash for messages
from app.forms.user_form import UserForm
from app.models import User, db  # Import db for database operations

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
    if form.validate_on_submit():
        # Add user to the database
        new_user = User(
            staffno=form.staffno.data,
            staffname=form.staffname.data,
            isadmin=form.isadmin.data,
            password_hash=User.set_password(password=form.password.data)
        )
        db.session.add(new_user)
        db.session.commit()
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
