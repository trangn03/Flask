# Import necessary modules
from flask import Flask, request, jsonify  # Flask for creating the web app, request for handling incoming requests, jsonify for formatting responses
from flask_sqlalchemy import SQLAlchemy  # SQLAlchemy for ORM (Object Relational Mapping) to interact with the database
import re  # Regular expression module for validation

app = Flask(__name__)  # Create a new Flask application instance

# Configuration for connecting to the MySQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Prema$1998@localhost/student_management'  # URI for MySQL database connection
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable tracking modifications for performance optimization

# Initialize the SQLAlchemy database object
db = SQLAlchemy(app)

# Define the 'Student' model to interact with the 'students' table in the database
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key for the student
    name = db.Column(db.String(50), nullable=False)  # Name of the student (cannot be null)
    age = db.Column(db.Integer, nullable=False)  # Age of the student (cannot be null)
    address = db.Column(db.String(255), nullable=False)  # Address of the student (cannot be null)
    email = db.Column(db.String(100), nullable=False, unique=True)  # Email (unique and cannot be null)
    subject = db.Column(db.String(100), nullable=False)  # Subject the student is studying (cannot be null)
    semester = db.Column(db.Integer, nullable=False)  # Semester number (cannot be null)

    def __init__(self, name, age, address, email, subject, semester):  
        self.name = name  
        self.age = age  
        self.address = address  
        self.email = email  
        self.subject = subject
        self.semester = semester

    # Method to serialize the student object to a dictionary
    def serialize(self):  
        return {
            "id": self.id,  
            "name": self.name,  
            "age": self.age,  
            "address": self.address,  
            "email": self.email,  
            "subject": self.subject,
            "semester": self.semester
        }

# Define the 'User' model for user registration and authentication
class User(db.Model):  
    id = db.Column(db.Integer, primary_key=True)  # Primary key for the user
    username = db.Column(db.String(50), nullable=False, unique=True)  # Username (must be unique)
    password = db.Column(db.String(255), nullable=False)  # Password (cannot be null)

    def __init__(self, username, password):  
        self.username = username  
        self.password = password  

# Create the tables in the database (only if they don't exist already)
with app.app_context():  
    db.create_all()

# Validate email format using a regular expression
def validate_email(email):  
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'  # Regex pattern for valid email
    return re.match(email_regex, email)  # Return a match object if the email matches the pattern, otherwise None

# Validate password rules (length, digits, letters, special characters)
def validate_password(password):
    if len(password) < 8:  # Password must be at least 8 characters long
        return "Password must be at least 8 characters long."
    if not re.search(r'\d', password):  # Password must contain at least one digit
        return "Password must contain at least one digit."
    if not re.search(r'[A-Z]', password):  # Password must contain at least one uppercase letter
        return "Password must contain at least one uppercase letter."
    if not re.search(r'[a-z]', password):  # Password must contain at least one lowercase letter
        return "Password must contain at least one lowercase letter."
    if not re.search(r'[\W_]', password):  # Password must contain at least one special character (non-alphanumeric)
        return "Password must contain at least one special character."
    return None  # Return None if password is valid

# Route for user registration (POST request)
@app.route('/register', methods=['POST'])
def register():
    # Check if username and password are provided in the request
    if not request.json or 'username' not in request.json or 'password' not in request.json:
        return jsonify({'error': 'Username and password are required'}), 400  # Return error if any of them is missing
    
    username = request.json['username']  # Extract the username from the request
    password = request.json['password']  # Extract the password from the request
    
    # Validate the password
    password_error = validate_password(password)
    if password_error:
        return jsonify({'error': password_error}), 400  # Return error if password is invalid
    
    # Check if the username already exists in the database
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'User already exists'}), 400  # Return error if user already exists

    # Create a new user and add it to the database
    new_user = User(username=username, password=password)  
    db.session.add(new_user)  # Add the new user to the session
    db.session.commit()  # Commit the session to save the new user to the database
    
    return jsonify({'message': 'User registered successfully'}), 201  # Return success message

# Route for user login (POST request)
@app.route('/login', methods=['POST'])
def login():
    # Check if username and password are provided in the request
    if not request.json or 'username' not in request.json or 'password' not in request.json:
        return jsonify({'error': 'Username and password are required'}), 400  # Return error if any of them is missing
    
    username = request.json['username']  # Extract the username from the request
    password = request.json['password']  # Extract the password from the request

    # Look for the user in the database
    user = User.query.filter_by(username=username).first()  
    if user is None or user.password != password:  # Check if user exists and if password matches
        return jsonify({'error': 'Invalid credentials'}), 401  # Return error if credentials are invalid

    return jsonify({'message': 'Login successful'}), 200  # Return success message

# Route to create a new student (POST request)
@app.route('/students', methods=['POST'])  
def create_student():
    # Check if all required fields are provided in the request
    if not request.json or 'name' not in request.json or 'age' not in request.json or 'address' not in request.json or 'email' not in request.json or 'subject' not in request.json or 'semester' not in request.json:
        return jsonify({'error': 'Please provide name, age, address, email, subject, and semester'}), 400  # Return error if any field is missing

    name = request.json['name'].strip()  # Extract and strip leading/trailing spaces from name
    age = request.json['age']  # Extract age
    address = request.json['address'].strip()  # Extract and strip leading/trailing spaces from address
    email = request.json['email'].strip()  # Extract and strip leading/trailing spaces from email
    subject = request.json['subject'].strip()  # Extract and strip leading/trailing spaces from subject
    semester = request.json['semester']  # Extract semester
    
    # Validate fields
    if not name:  
        return jsonify({'error': 'Name cannot be empty'}), 400  # Return error if name is empty
    if not address:  
        return jsonify({'error': 'Address cannot be empty'}), 400  # Return error if address is empty
    if not isinstance(age, int) or age <= 0 or age > 100:  
        return jsonify({'error': 'Age must be a positive number between 1 and 100'}), 400  # Validate age
    if not validate_email(email):  
        return jsonify({'error': 'Invalid email format'}), 400  # Validate email format
    if not subject:  
        return jsonify({'error': 'Subject cannot be empty'}), 400  # Return error if subject is empty
    if not isinstance(semester, int) or semester < 1 or semester > 8:  
        return jsonify({'error': 'Semester must be an integer between 1 and 8'}), 400  # Validate semester

    # Create and add a new student to the database
    new_student = Student(name=name, age=age, address=address, email=email, subject=subject, semester=semester)
    db.session.add(new_student)  # Add the new student to the session
    db.session.commit()  # Commit the session to save the new student to the database
    return jsonify(new_student.serialize()), 201  # Return the serialized student data

# Route to update a student's information (PUT request)
@app.route('/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    # Look for the student by their ID
    student = Student.query.get(student_id)
    if student is None:  
        return jsonify({'error': 'Student not found'}), 404  # Return error if student is not found

    # Extract data from the request
    data = request.json  
    if 'age' in data and (not isinstance(data['age'], int) or data['age'] <= 0 or data['age'] > 100):  
        return jsonify({'error': 'Age must be a positive number between 1 and 100'}), 400  # Validate age
    if 'email' in data and not validate_email(data['email']):  
        return jsonify({'error': 'Invalid email format'}), 400  # Validate email
    if 'semester' in data and (not isinstance(data['semester'], int) or data['semester'] < 1 or data['semester'] > 8):  
        return jsonify({'error': 'Semester must be an integer between 1 and 8'}), 400  # Validate semester

    # Update the student information with the provided data
    student.name = data.get('name', student.name)
    student.age = data.get('age', student.age)
    student.address = data.get('address', student.address)
    student.email = data.get('email', student.email)
    student.subject = data.get('subject', student.subject)
    student.semester = data.get('semester', student.semester)

    db.session.commit()  # Commit the changes to the database
    return jsonify(student.serialize())  # Return the updated student data

# Route to delete a student (DELETE request)
@app.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    # Look for the student by their ID
    student = Student.query.get(student_id)
    if student is None:  
        return jsonify({'error': 'Student not found'}), 404  # Return error if student is not found

    # Delete the student from the database
    db.session.delete(student)  
    db.session.commit()  # Commit the deletion to the database
    return jsonify({'message': 'Student deleted successfully'}), 200  # Return success message