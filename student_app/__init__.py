from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    login_manager.init_app(app)
    
    from student_app.routes.auth import auth as auth_blueprint
    from student_app.routes.courses import courses as courses_blueprint
    from student_app.routes.assignments import assignments as assignments_blueprint
    from student_app.routes.users import users as users_blueprint
    
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(courses_blueprint)
    app.register_blueprint(assignments_blueprint)
    app.register_blueprint(users_blueprint)
    
    with app.app_context():
        db.create_all()
    
    return app