import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Add the current directory to sys.path if it's not already there
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard-to-guess-string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///student_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)

# Simple route to test
@app.route('/')
def hello():
    return 'Flask is working!'

if __name__ == '__main__':
    app.run(debug=True)