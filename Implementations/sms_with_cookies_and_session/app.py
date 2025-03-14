from flask import Flask, request, jsonify, session
import re
from datetime import timedelta

# Initialize the Flask application
app = Flask(__name__)

# Session configuration
app.config['SECRET_KEY'] = 'sanjay'  # Secret key for encrypting session cookies
app.config['SESSION_COOKIE_NAME'] = 'student_app_session'  # Name of session cookie
app.config['SESSION_PERMANENT'] = False  # Session will not be permanent
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Session expires after 30 minutes
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevents JavaScript access to session cookie
app.config['SESSION_COOKIE_SECURE'] = False  # Should be True in production for HTTPS security

# In-memory data storage for students and users
students = [  # List to store student records
    {"id": 1, "name": "Sanjay", "age": 24, "email": "sanjay@gmail.com", "class": "web-backend-engineering", "location": "fullerton", "semester": 6},
    {"id": 2, "name": "Kalea", "age": 22, "email": "kalea@gmail.com", "class": "Web-front end engineering", "location": "Riverside", "semester": 5}
]

users = {}  # Dictionary to store user credentials

# Helper function to find a student by ID
def find_student(student_id):
    return next((student for student in students if student["id"] == student_id), None)

# Helper function to validate email addresses using regex
def is_valid_email(email):
    return re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email)

# User registration endpoint
@app.route('/register', methods=['POST'])
def register():
    if not request.json or 'username' not in request.json or 'password' not in request.json:
        return jsonify({'error': 'Username and password are required'}), 400
    
    username = request.json['username']
    password = request.json['password']
    
    if username in users:
        return jsonify({'error': 'User already exists'}), 400
    
    if len(password) < 8 or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return jsonify({'error': 'Password must be at least 8 characters long and contain at least one special character'}), 400
    
    users[username] = password  # Store user credentials
    return jsonify({'message': 'User registered successfully'}), 201

# User login endpoint
@app.route('/login', methods=['POST'])
def login():
    if not request.json or 'username' not in request.json or 'password' not in request.json:
        return jsonify({'error': 'Username and password are required'}), 400
    
    username = request.json['username']
    password = request.json['password']
    
    if users.get(username) != password:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    session['user'] = username  # Store user session
    response = jsonify({'message': 'Login successful'})
    response.set_cookie('username', username, httponly=True, max_age=1800)  # Set session cookie
    return response, 200

# User logout endpoint
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)  # Remove user session
    response = jsonify({'message': 'Logout successful'})
    response.set_cookie('username', '', expires=0)  # Clear session cookie
    return response, 200

# Middleware to protect routes, allowing only logged-in users
@app.before_request
def require_login():
    allowed_routes = ['login', 'register']  # Routes that don't require authentication
    if request.endpoint not in allowed_routes and 'user' not in session:
        return jsonify({'error': 'Unauthorized access. Please log in to view this resource.'}), 401

# Get all students (only if logged in)
@app.route('/students', methods=['GET'])
def get_students():
    return jsonify(students)

# Get a single student by ID (only if logged in)
@app.route('/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    student = find_student(student_id)
    if student is None:
        return jsonify({'error': 'Student not found'}), 404
    return jsonify(student)

# Create a new student entry (only if logged in)
@app.route('/students', methods=['POST'])
def create_student():
    required_fields = ['name', 'age', 'email', 'class', 'location', 'semester']
    if not request.json or not all(field in request.json for field in required_fields):
        return jsonify({'error': 'All fields are required'}), 400
    
    student_id = max(student['id'] for student in students) + 1 if students else 1
    student = {**request.json, 'id': student_id}
    students.append(student)
    return jsonify(student), 201

# Update an existing student record (only if logged in)
@app.route('/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    student = find_student(student_id)
    if student is None:
        return jsonify({'error': 'Student not found'}), 404
    
    student.update(request.json)
    return jsonify(student)

# Delete a student by ID (only if logged in)
@app.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    student = find_student(student_id)
    if student is None:
        return jsonify({'error': 'Student not found'}), 404
    
    students.remove(student)
    return jsonify({'message': 'Student deletion successful'}), 200

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)