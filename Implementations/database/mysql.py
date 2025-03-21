# Import necessary modules
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)

# Configuration for connecting to the MySQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Trang637603%40@localhost/student_management'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy database object
db = SQLAlchemy(app)

# Define the 'Student' model to interact with the 'students' table in the database
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    subject = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    branch = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(10), nullable=False)

    def __init__(self, name, age, address, email, subject, semester, branch, phone_number):
        self.name = name
        self.age = age
        self.address = address
        self.email = email
        self.subject = subject
        self.semester = semester
        self.branch = branch
        self.phone_number = phone_number

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "address": self.address,
            "email": self.email,
            "subject": self.subject,
            "semester": self.semester,
            "branch": self.branch,
            "phone_number": self.phone_number
        }

# Define the 'User' model for user registration and authentication
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

# Create the tables in the database (only if they don't exist already)
with app.app_context():
    db.create_all()

# Validation functions
def validate_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email)

def validate_password(password):
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r'\d', password):
        return "Password must contain at least one digit."
    if not re.search(r'[A-Z]', password):
        return "Password must contain at least one uppercase letter."
    if not re.search(r'[a-z]', password):
        return "Password must contain at least one lowercase letter."
    if not re.search(r'[\W_]', password):
        return "Password must contain at least one special character."
    return None

def validate_branch(branch):
    if not isinstance(branch, str):
        return "branch shall be a string"
    return None

def validate_phone_number(phone_number):
    if not str(phone_number).isdigit() or len(str(phone_number)) != 10:
        return "phone number should be of length 10"
    return None

def validate_student_data(data, partial=False):
    errors = {}

    # For partial updates (PUT), only validate fields that are provided
    if not partial:
        if 'name' not in data or not data['name'].strip():
            errors['name'] = "Name cannot be empty"
    elif 'name' in data and not data['name'].strip():
        errors['name'] = "Name cannot be empty"

    if 'age' in data:
        if not isinstance(data['age'], int) or data['age'] <= 0 or data['age'] > 100:
            errors['age'] = "Age must be a positive number between 1 and 100"

    if not partial:
        if 'address' not in data or not data['address'].strip():
            errors['address'] = "Address cannot be empty"
    elif 'address' in data and not data['address'].strip():
        errors['address'] = "Address cannot be empty"

    if 'email' in data and not validate_email(data['email']):
        errors['email'] = "Invalid email format"

    if not partial:
        if 'subject' not in data or not data['subject'].strip():
            errors['subject'] = "Subject cannot be empty"
    elif 'subject' in data and not data['subject'].strip():
        errors['subject'] = "Subject cannot be empty"

    if 'semester' in data:
        if not isinstance(data['semester'], int) or data['semester'] < 1 or data['semester'] > 8:
            errors['semester'] = "Semester must be an integer between 1 and 8"

    if 'branch' in data:
        branch_error = validate_branch(data['branch'])
        if branch_error:
            errors['branch'] = branch_error

    if 'phone_number' in data:
        phone_error = validate_phone_number(data['phone_number'])
        if phone_error:
            errors['phone_number'] = phone_error

    if not partial:
        # For POST requests, ensure all required fields are present
        required_fields = ['name', 'age', 'address', 'email', 'subject', 'semester', 'branch', 'phone_number']
        for field in required_fields:
            if field not in data:
                errors[field] = f"{field.capitalize()} is required"

    return errors if errors else None

# Route for user registration (POST request)
@app.route('/register', methods=['POST'], strict_slashes=False)
def register():
    if not request.json or 'username' not in request.json or 'password' not in request.json:
        return jsonify({'error': 'Username and password are required'}), 400
    
    username = request.json['username']
    password = request.json['password']
    
    password_error = validate_password(password)
    if password_error:
        return jsonify({'error': password_error}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'User already exists'}), 400

    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully'}), 201

# Route for user login (POST request)
@app.route('/login', methods=['POST'], strict_slashes=False)
def login():
    if not request.json or 'username' not in request.json or 'password' not in request.json:
        return jsonify({'error': 'Username and password are required'}), 400
    
    username = request.json['username']
    password = request.json['password']

    user = User.query.filter_by(username=username).first()
    if user is None or user.password != password:
        return jsonify({'error': 'Invalid credentials'}), 401

    return jsonify({'message': 'Login successful'}), 200

# Route to create a new student (POST request)
@app.route('/students', methods=['POST'], strict_slashes=False)
def create_student():
    data = request.json
    validation_errors = validate_student_data(data)

    if validation_errors:
        return jsonify({'error': validation_errors}), 400

    # Create and add a new student to the database
    new_student = Student(
        name=data['name'].strip(),
        age=data['age'],
        address=data['address'].strip(),
        email=data['email'].strip(),
        subject=data['subject'].strip(),
        semester=data['semester'],
        branch=data['branch'],
        phone_number=data['phone_number']
    )
    db.session.add(new_student)
    db.session.commit()
    return jsonify(new_student.serialize()), 201

# Route to update a student's information (PUT request)
@app.route('/students/<int:student_id>', methods=['PUT'], strict_slashes=False)
def update_student(student_id):
    student = Student.query.get(student_id)
    if student is None:
        return jsonify({'error': 'Student not found'}), 404

    data = request.json
    validation_errors = validate_student_data(data, partial=True)
    if validation_errors:
        return jsonify({'error': validation_errors}), 400

    # Update the student information with the provided data
    student.name = data.get('name', student.name)
    student.age = data.get('age', student.age)
    student.address = data.get('address', student.address)
    student.email = data.get('email', student.email)
    student.subject = data.get('subject', student.subject)
    student.semester = data.get('semester', student.semester)
    student.branch = data.get('branch', student.branch)
    student.phone_number = data.get('phone_number', student.phone_number)

    db.session.commit()
    return jsonify(student.serialize())

# Route to delete a student (DELETE request)
@app.route('/students/<int:student_id>', methods=['DELETE'], strict_slashes=False)
def delete_student(student_id):
    student = Student.query.get(student_id)
    if student is None:
        return jsonify({'error': 'Student not found'}), 404

    db.session.delete(student)
    db.session.commit()
    return jsonify({'message': 'Student deleted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)