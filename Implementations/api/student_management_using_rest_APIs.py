from flask import Flask, request, jsonify, session
import re

# Create a Flask application instance
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sanjay'

# In-memory database (list of dictionaries) to store student records
students = [
    {"id": 1, "name": "Sanjay", "age": 24, "email": "sanjay@gmail.com", "class": "web-backend-engineering", "location": "fullerton", "semester": 6},
    {"id": 2, "name": "kalea", "age": 22, "email": "kalea@gmail.com", "class": "Web-front end engineering", "location": "Riverside", "semester": 5}
]

# In-memory user storage
users = {}


# Route to create an account
@app.route('/register', methods=['POST'])
def register():
    if not request.json or 'username' not in request.json or 'password' not in request.json:
        return jsonify({'error': 'Username and password are required'}), 400
    
    username = request.json['username']
    password = request.json['password']
    
    if not isinstance(username, str):
        return jsonify({'error': 'Username must be a string'}), 400
    if len(password) < 8 or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return jsonify({'error': 'Password must be at least 8 characters long and contain at least one special character'}), 400
    
    if username in users:
        return jsonify({'error': 'User already exists'}), 400
    
    users[username] = password
    return jsonify({'message': 'User registered successfully'}), 201

# Route to login
@app.route('/login', methods=['POST'])
def login():
    if not request.json or 'username' not in request.json or 'password' not in request.json:
        return jsonify({'error': 'Username and password are required'}), 400
    
    username = request.json['username']
    password = request.json['password']
    
    if users.get(username) != password:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    session['user'] = username
    return jsonify({'message': 'Login successful'}), 200

# Route to logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'message': 'Logout successful'}), 200

# Helper function to find a student by ID
def find_student(student_id):
    for student in students:
        if student["id"] == student_id:
            return student
    return None

# Validation function
def is_valid_email(email):
    return re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email)

# Route to GET all students
@app.route('/students', methods=['GET'])
def get_students():
    return jsonify(students)

# Route to GET a specific student by ID
@app.route('/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    student = find_student(student_id)
    if student is None:
        return jsonify({'error': 'Student not found'}), 404
    return jsonify(student)

# Route to POST (Create) a new student
@app.route('/students', methods=['POST'])
def create_student():
    required_fields = ['name', 'age', 'email', 'class', 'location', 'semester']
    if not request.json or not all(field in request.json for field in required_fields):
        return jsonify({'error': 'All fields are required: name, age, email, class, location, semester'}), 400
    
    if not isinstance(request.json['name'], str):
        return jsonify({'error': 'Name must be a string'}), 400
    if not isinstance(request.json['class'], str):
        return jsonify({'error': 'Class must be a string'}), 400
    if not isinstance(request.json['location'], str):
        return jsonify({'error': 'Location must be a string'}), 400
    if not isinstance(request.json['semester'], int) or not (1 <= request.json['semester'] <= 8):
        return jsonify({'error': 'Semester must be an integer between 1 and 8'}), 400
    if not isinstance(request.json['age'], int) or not (16 <= request.json['age'] <= 99):
        return jsonify({'error': 'Age must be an integer between 16 and 99'}), 400
    if not is_valid_email(request.json['email']):
        return jsonify({'error': 'Invalid email format'}), 400
    
    student_id = max(student['id'] for student in students) + 1 if students else 1
    student = {
        'id': student_id,
        'name': request.json['name'],
        'age': request.json['age'],
        'email': request.json['email'],
        'class': request.json['class'],
        'location': request.json['location'],
        'semester': request.json['semester']
    }
    students.append(student)
    return jsonify(student), 201


# Route to PUT (Update) an existing student
@app.route('/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    student = find_student(student_id)
    if student is None:
        return jsonify({'error': 'Student not found'}), 404
    
    if not request.json:
        return jsonify({'error': 'Request body must be JSON'}), 400
    
    if 'name' in request.json and not isinstance(request.json['name'], str):
        return jsonify({'error': 'Name must be a string'}), 400
    if 'class' in request.json and not isinstance(request.json['class'], str):
        return jsonify({'error': 'Class must be a string'}), 400
    if 'location' in request.json and not isinstance(request.json['location'], str):
        return jsonify({'error': 'Location must be a string'}), 400
    if 'email' in request.json and not is_valid_email(request.json['email']):
        return jsonify({'error': 'Invalid email format'}), 400
    if 'semester' in request.json and (not isinstance(request.json['semester'], int) or not (1 <= request.json['semester'] <= 8)):
        return jsonify({'error': 'Semester must be an integer between 1 and 8'}), 400
    if 'age' in request.json and (not isinstance(request.json['age'], int) or not (16 <= request.json['age'] <= 99)):
        return jsonify({'error': 'Age must be an integer between 16 and 99'}), 400
    
    student.update(request.json)
    return jsonify(student)


# Route to DELETE a student by ID
@app.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    student = find_student(student_id)
    if student is None:
        return jsonify({'error': 'Student not found'}), 404
    students.remove(student)
    return jsonify({'message': 'Student deletion successful'}), 200

# Entry point for running the application
if __name__ == '__main__':
    app.run(debug=True)