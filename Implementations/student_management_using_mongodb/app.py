from flask import Flask, request, jsonify  # Import necessary components from Flask for creating the web app and handling requests
from pymongo import MongoClient  # Import MongoClient to connect to MongoDB
from bson import ObjectId  # Import ObjectId to handle MongoDB's unique identifiers
import re  # Import re for regular expressions to validate email formats

app = Flask(__name__)  # Create an instance of the Flask application

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")  # Establish a connection to the MongoDB server
db = client['student_db']  # Select the student_db database (will be created if it doesn't exist)
students_collection = db['students']  # Select the students collection within the database

def validate_email(email):  # Define a function to validate email addresses
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'  # Regex pattern for validating emails
    return re.match(email_regex, email)  # Return the result of the regex match

def serialize_student(student):  # Define a function to serialize student documents
    student['_id'] = str(student['_id'])  # Convert ObjectId to string for JSON serialization
    return student  # Return the serialized student document

@app.route('/students', methods=['GET'])  # Define a route for GET requests to retrieve all students
def get_students():  # Define the function to handle GET requests for all students
    students = list(students_collection.find())  # Fetch all student documents from the database
    return jsonify([serialize_student(student) for student in students])  # Serialize and return the student documents as a JSON response

@app.route('/students/<student_id>', methods=['GET'])  # Define a route for GET requests to retrieve a specific student by ID
def get_student(student_id):  # Define the function to handle GET requests for a specific student
    try:  # Start a try block to handle exceptions
        student = students_collection.find_one({"_id": ObjectId(student_id)})  # Find the student document by its ID
        if not student:  # Check if the student was found
            return jsonify({'error': 'Student not found'}), 404  # Return error if not found
        return jsonify(serialize_student(student))  # Return the serialized student document as a JSON response
    except Exception as e:  # Catch any exceptions
        return jsonify({'error': str(e)}), 400  # Return an error for invalid ObjectId with a 400 status code

@app.route('/students', methods=['POST'])  # Define a route for POST requests to create a new student
def create_student():  # Define the function to handle POST requests for creating a student
    if not request.json or 'name' not in request.json or 'age' not in request.json or 'address' not in request.json or 'email' not in request.json:  # Check if required fields are provided
        return jsonify({'error': 'Please provide name, age, address, and email'}), 400  # Return error if required fields are missing

    age = request.json['age']  # Extract age from the request
    email = request.json['email']  # Extract email from the request

    # Validate age
    if not isinstance(age, int) or age <= 0 or age > 100:  # Check if age is a valid number
        return jsonify({'error': 'Age must be a positive number between 1 and 100'}), 400  # Return error if age is invalid

    # Validate email
    if not validate_email(email):  # Check if the email format is valid
        return jsonify({'error': 'Invalid email format'}), 400  # Return error if email is invalid

    student = {  # Create a student dictionary from the request data
        'name': request.json['name'],  # Set the name
        'age': age,  # Set the age
        'address': request.json['address'],  # Set the address
        'email': email  # Set the email
    }
    
    result = students_collection.insert_one(student)  # Insert the student into the database
    student['_id'] = str(result.inserted_id)  # Get the generated ObjectId and convert it to a string
    return jsonify(serialize_student(student)), 201  # Return the serialized student document with a 201 status code

@app.route('/students/<student_id>', methods=['PUT'])  # Define a route for PUT requests to update a specific student by ID
def update_student(student_id):  # Define the function to handle PUT requests for updating a student
    try:  # Start a try block to handle exceptions
        student = students_collection.find_one({"_id": ObjectId(student_id)})  # Find the student document by its ID
        if not student:  # Check if the student was found
            return jsonify({'error': 'Student not found'}), 404  # Return error if not found

        updated_data = {  # Create a dictionary for the updated student data
            'name': request.json.get('name', student['name']),  # Update name if provided, else keep the existing one
            'age': request.json.get('age', student['age']),  # Update age if provided, else keep the existing one
            'address': request.json.get('address', student['address']),  # Update address if provided, else keep the existing one
            'email': request.json.get('email', student['email']),  # Update email if provided, else keep the existing one
        }

        # Validate age
        if 'age' in request.json and (not isinstance(updated_data['age'], int) or updated_data['age'] <= 0 or updated_data['age'] > 100):  # Check if the updated age is valid
            return jsonify({'error': 'Age must be a positive number between 1 and 100'}), 400  # Return error if age is invalid

        # Validate email
        if 'email' in request.json and not validate_email(updated_data['email']):  # Check if the updated email format is valid
            return jsonify({'error': 'Invalid email format'}), 400  # Return error if email is invalid

        students_collection.update_one({"_id": ObjectId(student_id)}, {"$set": updated_data})  # Update the student document in the database
        return jsonify(serialize_student(updated_data))  # Return the serialized updated student document
    except Exception as e:  # Catch any exceptions
        return jsonify({'updated': str(e)}), 400  # Return an error for invalid ObjectId with a 400 status code

@app.route('/students/<student_id>', methods=['DELETE'])  # Define a route for DELETE requests to delete a specific student by ID
def delete_student(student_id):  # Define the function to handle DELETE requests for deleting a student
    try:  # Start a try block to handle exceptions
        result = students_collection.delete_one({"_id": ObjectId(student_id)})  # Attempt to delete the student document by its ID
        if result.deleted_count == 0:  # Check if any document was deleted
            return jsonify({'error': 'Student not found'}), 404  # Return error if no document was deleted
        return jsonify({'success': 'Student deleted'}), 200  # Return success message with a 200 status code
    except Exception as e:  # Catch any exceptions
        return jsonify({'error': str(e)}), 400  # Return an error for invalid ObjectId with a 400 status code

if __name__ == "__main__":  # Check if the script is being run directly
    app.run(debug=True)  # Start the Flask application with debugging enabled
