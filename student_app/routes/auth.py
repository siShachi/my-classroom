from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from student_app.models import User
from student_app import db
from werkzeug.urls import url_parse
import redis as Redis
import os
LOGIN_FAILURE_LIMIT = 3
redis = Redis.Redis(host=os.environ.get("REDIS_HOST"), port=os.environ.get("REDIS_PORT"), db=0)

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('courses.index'))
     # Check if login failures are too high
    ip = request.remote_addr
    if redis.get(f"student_app:login_failures:{ip}"):
        if int(redis.get(f"student_app:login_failures:{ip}")) >= LOGIN_FAILURE_LIMIT:
            return "Too many login failures. Please try again later after some time.", 401
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            ip = request.remote_addr
            if redis.get(f"student_app:login_failures:{ip}") is None:
                redis.set(f"student_app:login_failures:{ip}", 1, ex=3600)
            else:
                redis.incr(f"student_app:login_failures:{ip}")
                if int(redis.get(f"student_app:login_failures:{ip}")) >= LOGIN_FAILURE_LIMIT:
                    flash('Too many login failures. Please try again later.')
                    return redirect(url_for('auth.login'))
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        flash(f'Welcome back, {user.first_name} {user.last_name}!', 'login_success')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('courses.index')
        return redirect(next_page)
    
    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('courses.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        role = request.form.get('role', 'student')
        
        # Check if user already exists
        user_email = User.query.filter_by(email=email).first()
        user_username = User.query.filter_by(username=username).first()
        
        if user_email:
            flash('Email already exists.')
            return redirect(url_for('auth.register'))
        
        if user_username:
            flash('Username already exists.')
            return redirect(url_for('auth.register'))
        
        # Create new user
        new_user = User(email=email, username=username, first_name=first_name, last_name=last_name, role=role)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))