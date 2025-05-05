import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from student_app import create_app
    print("Successfully imported create_app!")
    
    app = create_app()
    print("Successfully created app!")
except Exception as e:
    print(f"Error: {e}")