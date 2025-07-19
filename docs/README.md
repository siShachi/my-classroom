## Environment Setup

### Creating a Virtual Environment
First create a virtual environment using the following command:
```bash
python -m venv env
```

### Activating the Virtual Environment
After that activate the virtual environment using the following command:
```bash
.\env\Scripts\activate
```

### Installing Python Packages
Then install the required python packages using the following command:
```bash
pip install -r requirements.txt
```
### Creating the .env file
Create a .env file in the root directory of the project by copying the example template and add the according values to it:
```bash
cp .env.example .env
nano .env
```
Then save the file (Ctrl+O) and exit (Ctrl+X).


## Running the Application
### To run the application in development mode, use the following command:
To run the application in development mode, use the following command:
```bash
python run.py
```
This will start the application in development mode on port 5000.
### To run the application in production mode, use the following command:
To run the application in production mode, use the following command:
```bash
uvicorn run:app --reload --port 80
```
Here `80` is the port number that will be used to run the application. You can change it to any other port number.
