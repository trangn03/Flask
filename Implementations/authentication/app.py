from flask import Flask, request, jsonify, make_response
import jwt  # For encoding and decoding tokens
import datetime  # For expiration handling
from functools import wraps

app = Flask(__name__)

# Secret key to encode the JWT (store it securely in production)
app.config['SECRET_KEY'] = 'CPSC449'

# Helper function to check if the request has a valid JWT token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')  # Get the token from headers

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401  # Unauthorized

        try:
            # Decode the token using the secret key
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data['username']  # Extract user info (username in this case)
        except:
            return jsonify({'message': 'Token is invalid!'}), 401  # Unauthorized
        
        return f(current_user, *args, **kwargs)
    
    return decorated

# Route to login and get a JWT token
@app.route('/login', methods=['POST'])
def login():
    auth = request.json  # Get the request JSON data
    username = auth.get('username')
    password = auth.get('password')

    # Dummy user credentials for the example
    if username != 'sanjay' or password != 'revanna':
        return jsonify({'message': 'Invalid credentials!'}), 401  # Unauthorized

    # Generate JWT token valid for 30 minutes
    token = jwt.encode(
        {'username': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
        app.config['SECRET_KEY'],
        algorithm="HS256"
    )

    return jsonify({'token': token})  # Return the generated token

# Protected route (requires valid JWT token)
@app.route('/protected', methods=['GET'])
@token_required
def protected_route(current_user):
    # The current_user is passed after token verification
    return jsonify({'message': f'Hello, {current_user}! Welcome to the CPSC449 class.'})

# Public route (does not require JWT token)
@app.route('/public', methods=['GET'])
def public_route():
    return jsonify({'message': 'This is a public route. Anyone can access it.'})

if __name__ == '__main__':
    app.run(debug=True)