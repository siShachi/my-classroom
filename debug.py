import sys
import os

# Print current working directory and Python path
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

# Try to import the app module
try:
    import student_app
    print(f"App module found at: {student_app.__file__}")
    
    # Check what's in the app module
    print(f"App module contents: {dir(student_app)}")
    
    # Try to import create_app directly
    try:
        from student_app import create_app
        print("Successfully imported create_app")
    except ImportError as e:
        print(f"Error importing create_app: {e}")
        
except ImportError as e:
    print(f"Error importing app module: {e}")