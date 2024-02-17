from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '2580',
    'database': 'USER'
}

# Function to connect to MySQL
def get_db():
    return mysql.connector.connect(**db_config)

# Home page
@app.route('/')
def home():
    if 'username' in session:
        return f'Hello, {session["username"]}! <a href="/logout">Logout</a>'
    return 'You are not logged in. <a href="/login">Login</a>'

# Signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Hash the password before storing it in the database (use a secure method in production)
        hashed_password = hash(password)

        try:
            db = get_db()
            cursor = db.cursor()

            # Check if the username already exists
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                return 'Username already exists. Choose a different username.'

            # Insert the new user into the database
            cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, hashed_password))
            db.commit()

            cursor.close()
            db.close()

            return redirect(url_for('login'))

        except Exception as e:
            return str(e)

    return render_template('signup.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            db = get_db()
            cursor = db.cursor()

            # Retrieve the user from the database
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            user = cursor.fetchone()

            if user and check_password(password, user[2]):
                # Set the username in the session to mark the user as logged in
                session['username'] = username
                return redirect(url_for('home'))
            else:
                return 'Invalid login credentials. Please try again.'

        except Exception as e:
            return str(e)

    return render_template('login.html')

# Logout page
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
