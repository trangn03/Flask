from flask import Flask, session, redirect, url_for, request, render_template

app = Flask(__name__)
app.secret_key = 'USA'  # Important for session security

@app.route('/')
def index():
    return render_template('login.html')  # This is your login form

@app.route('/login', methods=['POST'])
def login():
    session['username'] = request.form['username']  # Set session data
    return redirect(url_for('welcome'))

@app.route('/welcome')
def welcome():
    if 'username' in session:
        return render_template('welcome.html')  # Welcome page with a logout link
    else:
        return redirect(url_for('index'))  # Redirect if not logged in

@app.route('/logout')
def logout():
    # Clear the 'username' from session
    session.pop('username', None)
    return "You have been logged out!"
if __name__ == '__main__':
    app.run(debug=True)
