from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from student_app.models import Course, User, Announcement, Material
from student_app import db
import os
from werkzeug.utils import secure_filename
from config import Config

courses = Blueprint('courses', __name__, url_prefix='/courses')

@courses.route('/')
@login_required
def index():
    if current_user.role == 'instructor':
        my_courses = Course.query.filter_by(instructor_id=current_user.id).all()
    else:
        my_courses = current_user.enrolled_courses
    
    # For students, also show available courses to enroll
    available_courses = []
    if current_user.role == 'student':
        # Get all courses the student is not enrolled in
        all_courses = Course.query.all()
        available_courses = [c for c in all_courses if c not in my_courses]
    
    return render_template('courses/index.html', courses=my_courses, available_courses=available_courses)

@courses.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if current_user.role != 'instructor' and current_user.role != 'admin':
        flash('Only instructors can create courses.')
        return redirect(url_for('courses.index'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        code = request.form.get('code')
        description = request.form.get('description')
        
        # Check if course code already exists
        existing_course = Course.query.filter_by(code=code).first()
        if existing_course:
            flash('Course code already exists.')
            return redirect(url_for('courses.create'))
        
        new_course = Course(
            title=title,
            code=code,
            description=description,
            instructor_id=current_user.id
        )
        
        db.session.add(new_course)
        db.session.commit()
        
        flash('Course created successfully!')
        return redirect(url_for('courses.view', course_id=new_course.id))
    
    return render_template('courses/create.html')

@courses.route('/<int:course_id>')
@login_required
def view(course_id):
    course = Course.query.get_or_404(course_id)
    
    # Check if user is instructor or enrolled in the course
    if current_user.role != 'admin' and course.instructor_id != current_user.id and course not in current_user.enrolled_courses:
        flash('You are not enrolled in this course.')
        return redirect(url_for('courses.index'))
    
    announcements = Announcement.query.filter_by(course_id=course.id).order_by(Announcement.created_at.desc()).all()
    materials = Material.query.filter_by(course_id=course.id).order_by(Material.created_at.desc()).all()
    
    return render_template(
        'courses/view.html', 
        course=course, 
        announcements=announcements, 
        materials=materials
    )

@courses.route('/<int:course_id>/enroll')
@login_required
def enroll(course_id):
    if current_user.role != 'student':
        flash('Only students can enroll in courses.')
        return redirect(url_for('courses.index'))
    
    course = Course.query.get_or_404(course_id)
    
    if course in current_user.enrolled_courses:
        flash('You are already enrolled in this course.')
    else:
        current_user.enrolled_courses.append(course)
        db.session.commit()
        flash('Enrolled successfully!')
    
    return redirect(url_for('courses.view', course_id=course.id))

@courses.route('/<int:course_id>/unenroll')
@login_required
def unenroll(course_id):
    if current_user.role != 'student':
        flash('Only students can unenroll from courses.')
        return redirect(url_for('courses.index'))
    
    course = Course.query.get_or_404(course_id)
    
    if course in current_user.enrolled_courses:
        current_user.enrolled_courses.remove(course)
        db.session.commit()
        flash('Unenrolled successfully!')
    else:
        flash('You are not enrolled in this course.')
    
    return redirect(url_for('courses.index'))

@courses.route('/<int:course_id>/announcement', methods=['POST'])
@login_required
def add_announcement(course_id):
    course = Course.query.get_or_404(course_id)
    
    if current_user.role != 'admin' and course.instructor_id != current_user.id:
        flash('Only the instructor can add announcements.')
        return redirect(url_for('courses.view', course_id=course.id))
    
    title = request.form.get('title')
    content = request.form.get('content')
    
    announcement = Announcement(
        title=title,
        content=content,
        author_id=current_user.id,
        course_id=course.id
    )
    
    db.session.add(announcement)
    db.session.commit()
    
    flash('Announcement posted successfully!')
    return redirect(url_for('courses.view', course_id=course.id))

@courses.route('/<int:course_id>/material', methods=['POST'])
@login_required
def add_material(course_id):
    course = Course.query.get_or_404(course_id)
    
    if current_user.role != 'admin' and course.instructor_id != current_user.id:
        flash('Only the instructor can add materials.')
        return redirect(url_for('courses.view', course_id=course.id))
    
    title = request.form.get('title')
    description = request.form.get('description')
    file = request.files.get('file')
    
    if file and file.filename:
        filename = secure_filename(file.filename)
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)
        relative_path = f'uploads/{filename}'
    else:
        relative_path = None
    
    material = Material(
        title=title,
        description=description,
        file_path=relative_path,
        course_id=course.id
    )
    
    db.session.add(material)
    db.session.commit()
    
    flash('Material added successfully!')
    return redirect(url_for('courses.view', course_id=course.id))