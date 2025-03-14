from flask import Flask, request, jsonify  # Import necessary classes from Flask
from flask_sqlalchemy import SQLAlchemy  # Import SQLAlchemy for ORM capabilities
import re  # Import the regular expression module for email validation

app = Flask(__name__)  # Create an instance of the Flask application

# MySQL database connection configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Prema$1998@localhost/student_management'  # Define the database URI for MySQL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable tracking modifications for performance reasons

# Initialize the database
db = SQLAlchemy(app)  # Create an instance of SQLAlchemy with the Flask app

# Define the Student model (table schema)
class Student(db.Model):  # Create a Student class that represents the 'students' table
    id = db.Column(db.Integer, primary_key=True)  # Define the primary key 'id' as an Integer
    name = db.Column(db.String(50), nullable=False)  # Define 'name' as a String, cannot be null
    age = db.Column(db.Integer, nullable=False)  # Define 'age' as an Integer, cannot be null
    address = db.Column(db.String(255), nullable=False)  # Define 'address' as a String, cannot be null
    email = db.Column(db.String(100), nullable=False, unique=True)  # Define 'email' as a unique String, cannot be null

    def __init__(self, name, age, address, email):  # Constructor for initializing a Student object
        self.name = name  # Assign name
        self.age = age  # Assign age
        self.address = address  # Assign address
        self.email = email  # Assign email

    def serialize(self):  # Method to convert a Student object to a JSON-serializable format
        return {
            "id": self.id,  # Include 'id'
            "name": self.name,  # Include 'name'
            "age": self.age,  # Include 'age'
            "address": self.address,  # Include 'address'
            "email": self.email  # Include 'email'
        }

# Create the database and table when the app starts
with app.app_context():  # Use the app context to perform actions within the Flask application
    db.create_all()  # Create all tables defined by the models

# Function to validate email format
def validate_email(email):  # Define a function to validate email using regex
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'  # Define a regex pattern for valid emails
    return re.match(email_regex, email)  # Return a match object if the email is valid

# CRUD Operations

@app.route('/students', methods=['GET'])  # Define a route to get all students
def get_students():
    students = Student.query.all()  # Retrieve all students from the database
    return jsonify([student.serialize() for student in students])  # Return the serialized list of students as JSON

@app.route('/students/<int:student_id>', methods=['GET'])  # Define a route to get a specific student by ID
def get_student(student_id):
    student = Student.query.get(student_id)  # Retrieve student by ID
    if student is None:  # Check if student was not found
        return jsonify({'error': 'Student not found'}), 404  # Return error response if not found
    return jsonify(student.serialize())  # Return the serialized student as JSON

@app.route('/students', methods=['POST'])  # Define a route to create a new student
def create_student():
    # Check if the request contains the necessary JSON data
    if not request.json or 'name' not in request.json or 'age' not in request.json or 'address' not in request.json or 'email' not in request.json:
        return jsonify({'error': 'Please provide name, age, address, and email'}), 400  # Return error if data is missing

    age = request.json['age']  # Get the age from the request data
    email = request.json['email']  # Get the email from the request data

    # Validate age
    if not isinstance(age, int) or age <= 0 or age > 100:  # Check if age is a positive integer within 1-100
        return jsonify({'error': 'Age must be a positive number between 1 and 100'}), 400  # Return error if invalid

    # Validate email
    if not validate_email(email):  # Check if the email format is valid
        return jsonify({'error': 'Invalid email format'}), 400  # Return error if invalid

    # Create a new Student instance with the provided data
    new_student = Student(
        name=request.json['name'],
        age=age,
        address=request.json['address'],
        email=email
    )
    
    db.session.add(new_student)  # Add the new student to the session
    db.session.commit()  # Commit the session to save the student to the database

    return jsonify(new_student.serialize()), 201  # Return the serialized new student with 201 Created status

@app.route('/students/<int:student_id>', methods=['PUT'])  # Define a route to update a specific student by ID
def update_student(student_id):
    student = Student.query.get(student_id)  # Retrieve the student by ID
    if student is None:  # Check if student was not found
        return jsonify({'error': 'Student not found'}), 404  # Return error response if not found

    age = request.json.get('age', student.age)  # Get the new age from request or use the existing one
    email = request.json.get('email', student.email)  # Get the new email from request or use the existing one

    # Validate age
    if 'age' in request.json:  # Check if age is provided in the request
        if not isinstance(age, int) or age <= 0 or age > 100:  # Validate the age
            return jsonify({'error': 'Age must be a positive number between 1 and 100'}), 400  # Return error if invalid

    # Validate email
    if 'email' in request.json and not validate_email(email):  # Check if email is provided and valid
        return jsonify({'error': 'Invalid email format'}), 400  # Return error if invalid

    # Update the student fields with new values or keep existing values
    student.name = request.json.get('name', student.name)
    student.age = age
    student.address = request.json.get('address', student.address)
    student.email = email

    db.session.commit()  # Commit the changes to the database
    return jsonify(student.serialize())  # Return the updated student as JSON

@app.route('/students/<int:student_id>', methods=['DELETE'])  # Define a route to delete a specific student by ID
def delete_student(student_id):
    student = Student.query.get(student_id)  # Retrieve the student by ID
    if student is None:  # Check if student was not found
        return jsonify({'error': 'Student not found'}), 404  # Return error response if not found

    db.session.delete(student)  # Delete the student from the session
    db.session.commit()  # Commit the session to remove the student from the database

    return jsonify({'success': 'Student deleted'}), 200  # Return success message with 200 OK status

if __name__ == "__main__":  # Check if the script is run directly
    app.run(debug=True)  # Start the Flask application in debug mode for easier development
