from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from student_app.models import User
from student_app import db
from werkzeug.urls import url_parse
import redis as Redis
import os
LOGIN_FAILURE_LIMIT = 3
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
print("Redis URL: ", REDIS_URL)
redis = Redis.Redis.from_url(REDIS_URL)

auth = Blueprint('auth', __name__, url_prefix='/auth')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('courses.index'))

    ip = request.remote_addr
    failure_key = f"student_app:login_failures:{ip}"
    failure_count = redis.get(failure_key)
    if failure_count and int(failure_count) >= LOGIN_FAILURE_LIMIT:
        return "Too many login failures. Please try again later.", 401

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            # Handle login failure
            if failure_count is None:
                redis.set(failure_key, 1, ex=3600)  # expire after 1 hour
            else:
                redis.incr(failure_key)
                if int(redis.get(failure_key)) >= LOGIN_FAILURE_LIMIT:
                    flash('Too many login failures. Please try again later.')
                    return redirect(url_for('auth.login'))

            flash('Invalid email or password. Please try again.')
            return redirect(url_for('auth.login'))

        # Successful login
        login_user(user, remember=remember)
        redis.delete(failure_key)  # Reset on successful login
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

        # Check if email or username already exists
        if User.query.filter_by(email=email).first():
            flash('Email already exists.')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('auth.register'))

        # Create new user
        new_user = User(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
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
