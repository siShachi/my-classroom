from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from student_app.models import User, Course
from student_app import db

users = Blueprint('users', __name__, url_prefix='/users')

@users.route('/profile')
@login_required
def profile():
    return render_template('users/profile.html', user=current_user)

@users.route('/update', methods=['POST'])
@login_required
def update():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    
    current_user.first_name = first_name
    current_user.last_name = last_name
    
    db.session.commit()
    
    flash('Profile updated successfully!')
    return redirect(url_for('users.profile'))

@users.route('/change_password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not current_user.check_password(current_password):
        flash('Current password is incorrect.')
        return redirect(url_for('users.profile'))
    
    if new_password != confirm_password:
        flash('New passwords do not match.')
        return redirect(url_for('users.profile'))
    
    current_user.set_password(new_password)
    db.session.commit()
    
    flash('Password changed successfully!')
    return redirect(url_for('users.profile'))

@users.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        flash('Access denied.')
        return redirect(url_for('courses.index'))
    
    users_list = User.query.all()
    return render_template('users/admin.html', users=users_list)

@users.route('/admin/change_role/<int:user_id>', methods=['POST'])
@login_required
def change_role(user_id):
    if current_user.role != 'admin':
        flash('Access denied.')
        return redirect(url_for('courses.index'))
    
    user = User.query.get_or_404(user_id)
    role = request.form.get('role')
    
    user.role = role
    db.session.commit()
    
    flash(f'Role for {user.username} updated to {role}.')
    return redirect(url_for('users.admin_users'))