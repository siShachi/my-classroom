from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from student_app.models import Assignment, Submission, Course
from student_app import db
import os
from werkzeug.utils import secure_filename
from config import Config
from datetime import datetime

assignments = Blueprint('assignments', __name__, url_prefix='/assignments')

@assignments.route('/course/<int:course_id>')
@login_required
def index(course_id):
    course = Course.query.get_or_404(course_id)
    
    # Check if user is instructor or enrolled in the course
    if current_user.role != 'admin' and course.instructor_id != current_user.id and course not in current_user.enrolled_courses:
        flash('You are not enrolled in this course.')
        return redirect(url_for('courses.index'))
    
    assignments_list = Assignment.query.filter_by(course_id=course.id).order_by(Assignment.due_date.asc()).all()
    
    # For students, get submission status
    submissions = {}
    if current_user.role == 'student':
        for assignment in assignments_list:
            submission = Submission.query.filter_by(
                student_id=current_user.id, 
                assignment_id=assignment.id
            ).first()
            submissions[assignment.id] = submission
    
    return render_template(
        'assignments/index.html', 
        course=course, 
        assignments=assignments_list,
        submissions=submissions,
        now=datetime.utcnow()
    )

@assignments.route('/create/<int:course_id>', methods=['GET', 'POST'])
@login_required
def create(course_id):
    course = Course.query.get_or_404(course_id)
    
    if current_user.role != 'admin' and course.instructor_id != current_user.id:
        flash('Only the instructor can create assignments.')
        return redirect(url_for('assignments.index', course_id=course.id))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        due_date_str = request.form.get('due_date')
        points = request.form.get('points')
        
        due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M') if due_date_str else None
        
        assignment = Assignment(
            title=title,
            description=description,
            due_date=due_date,
            points=points,
            course_id=course.id
        )
        
        db.session.add(assignment)
        db.session.commit()
        
        flash('Assignment created successfully!')
        return redirect(url_for('assignments.index', course_id=course.id))
    
    return render_template('assignments/create.html', course=course)

@assignments.route('/<int:assignment_id>')
@login_required
def view(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    course = Course.query.get(assignment.course_id)
    
    # Check if user is instructor or enrolled in the course
    if current_user.role != 'admin' and course.instructor_id != current_user.id and course not in current_user.enrolled_courses:
        flash('You are not enrolled in this course.')
        return redirect(url_for('courses.index'))
    
    # For students, get their submission
    submission = None
    if current_user.role == 'student':
        submission = Submission.query.filter_by(
            student_id=current_user.id, 
            assignment_id=assignment.id
        ).first()
    
    # For instructors, get all submissions
    submissions = []
    if current_user.role in ['instructor', 'admin'] and course.instructor_id == current_user.id:
        submissions = Submission.query.filter_by(
            assignment_id=assignment.id
        ).all()
    
    return render_template(
        'assignments/view.html', 
        assignment=assignment, 
        course=course,
        submission=submission,
        submissions=submissions,
        now=datetime.utcnow()
    )

@assignments.route('/<int:assignment_id>/submit', methods=['GET', 'POST'])
@login_required
def submit(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    course = Course.query.get(assignment.course_id)
    
    if current_user.role != 'student':
        flash('Only students can submit assignments.')
        return redirect(url_for('assignments.view', assignment_id=assignment.id))
    
    if course not in current_user.enrolled_courses:
        flash('You are not enrolled in this course.')
        return redirect(url_for('courses.index'))
    
    existing_submission = Submission.query.filter_by(
        student_id=current_user.id, 
        assignment_id=assignment.id
    ).first()
    
    if request.method == 'POST':
        content = request.form.get('content')
        file = request.files.get('file')
        
        if file and file.filename:
            filename = secure_filename(f"{current_user.username}_{assignment.id}_{file.filename}")
            file_path = os.path.join(Config.UPLOAD_FOLDER, 'submissions', filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            file.save(file_path)
            relative_path = f'uploads/submissions/{filename}'
        else:
            relative_path = None if existing_submission is None else existing_submission.file_path
        
        if existing_submission:
            existing_submission.content = content
            if relative_path and file and file.filename:
                existing_submission.file_path = relative_path
            existing_submission.submitted_at = datetime.utcnow()
            
            db.session.commit()
            flash('Submission updated successfully!')
        else:
            submission = Submission(
                content=content,
                file_path=relative_path,
                student_id=current_user.id,
                assignment_id=assignment.id
            )
            
            db.session.add(submission)
            db.session.commit()
            flash('Assignment submitted successfully!')
        
        return redirect(url_for('assignments.view', assignment_id=assignment.id))
    
    return render_template(
        'assignments/submit.html', 
        assignment=assignment, 
        course=course,
        submission=existing_submission,
        now=datetime.utcnow()
    )

@assignments.route('/<int:assignment_id>/grade/<int:submission_id>', methods=['POST'])
@login_required
def grade(assignment_id, submission_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    course = Course.query.get(assignment.course_id)
    submission = Submission.query.get_or_404(submission_id)
    
    if current_user.role != 'admin' and course.instructor_id != current_user.id:
        flash('Only the instructor can grade assignments.')
        return redirect(url_for('assignments.view', assignment_id=assignment.id))
    
    grade = request.form.get('grade')
    feedback = request.form.get('feedback')
    
    submission.grade = grade
    submission.feedback = feedback
    
    db.session.commit()
    
    flash('Submission graded successfully!')
    return redirect(url_for('assignments.view', assignment_id=assignment.id))