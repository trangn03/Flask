from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
import re

app = Flask(__name__)

# MongoDB Configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/student_management"
mongo = PyMongo(app)

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
        return "Branch shall be a string"
    return None

def validate_phone_number(phone_number):
    if not str(phone_number).isdigit() or len(str(phone_number)) != 10:
        return "Phone number should be of length 10"
    return None

def validate_student_data(data):
    errors = {}

    if 'name' not in data or not re.match(r'^[a-zA-Z ]{2,}$', data['name']):
        errors['name'] = "Name must be at least 2 characters long and contain only alphabets."

    if 'age' not in data or not isinstance(data['age'], int) or data['age'] < 18 or data['age'] > 100:
        errors['age'] = "Age must be a number between 18 and 100."

    if 'address' not in data or not data['address'].strip():
        errors['address'] = "Address is required."

    if 'email' not in data or not validate_email(data['email']):
        errors['email'] = "Invalid email format."

    if 'subject' not in data or not data['subject'].strip():
        errors['subject'] = "Subject is required."

    if 'semester' not in data or not isinstance(data['semester'], int) or not (1 <= data['semester'] <= 8):
        errors['semester'] = "Semester must be a number between 1 and 8."
    
    if 'branch' not in data:
        errors['branch'] = "Branch is required."
    else:
        branch_error = validate_branch(data['branch'])
        if branch_error:
            errors['branch'] = branch_error

    if 'phone_number' not in data:
        errors['phone_number'] = "Phone number is required."
    else:
        phone_error = validate_phone_number(data['phone_number'])
        if phone_error:
            errors['phone_number'] = phone_error

    return errors if errors else None

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    if validate_password(password):
        return jsonify({'error': validate_password(password)}), 400
    
    if mongo.db.users.find_one({'username': username}):
        return jsonify({'error': 'User already exists'}), 400
    
    mongo.db.users.insert_one({'username': username, 'password': password})
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = mongo.db.users.find_one({'username': username})
    if not user or user['password'] != password:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    return jsonify({'message': 'Login successful'}), 200

@app.route('/students', methods=['POST'])
def create_student():
    data = request.json
    validation_errors = validate_student_data(data)

    if validation_errors:
        return jsonify({'error': validation_errors}), 400
    
    data['id'] = mongo.db.students.count_documents({}) + 1  # Generate ID manually
    mongo.db.students.insert_one(data)
    return jsonify({'message': 'Student added successfully'}), 201


@app.route('/students', methods=['GET'])
def get_students():
    students = mongo.db.students.find()  # Fetch all students
    student_list = []
    
    for student in students:
        student_list.append({
            "id": student["id"],  # Using manually assigned ID
            "name": student["name"],
            "age": student["age"],
            "address": student["address"],
            "email": student["email"],
            "subject": student["subject"],
            "semester": student["semester"],
            "branch": student["branch"],
            "phone_number": student["phone_number"],
        })
    
    return jsonify(student_list), 200


@app.route('/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    student = mongo.db.students.find_one({"id": student_id})
    
    if student:
        return jsonify({
            "id": student["id"],
            "name": student["name"],
            "age": student["age"],
            "address": student["address"],
            "email": student["email"],
            "subject": student["subject"],
            "semester": student["semester"],
            "branch": student["branch"],
            "phone_number": student["phone_number"],
        }), 200
    else:
        return jsonify({"error": "Student not found"}), 404

@app.route('/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    data = request.json
    student = mongo.db.students.find_one({'id': student_id})
    
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    validation_errors = validate_student_data(data)
    if validation_errors:
        return jsonify({'error': validation_errors}), 400
    
    mongo.db.students.update_one({'id': student_id}, {'$set': data})
    return jsonify({'message': 'Student updated successfully'}), 200

@app.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    student = mongo.db.students.find_one({'id': student_id})
    
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    mongo.db.students.delete_one({'id': student_id})
    return jsonify({'message': 'Student deleted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)