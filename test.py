import os
import sys

print("Current working directory:", os.getcwd())
print("Python path:", sys.path)

try:
    import student_app
    print("Successfully imported app module")
    print("App module location:", student_app.__file__)
except ImportError as e:
    print("Failed to import app module:", e)