import sqlite3
from flask import Flask, flash, redirect, url_for, render_template, request, session
from passlib.hash import sha256_crypt

app = Flask(__name__)
app.secret_key = "r@nd0mSk_1"
DATABASE = 'database.db'


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_db_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS login (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)')
    conn.commit()
    conn.close()


initialize_database()


def register_user_to_db(username, password, confirm_password):
    if password != confirm_password:
        flash("Passwords er ikke ens", 'error')
        return False  # Passwords do not match

    conn = get_db_connection()
    cur = conn.cursor()
    hashed_password = sha256_crypt.encrypt(password)
    cur.execute('INSERT INTO login (username, password) VALUES (?, ?)', (username, hashed_password))
    conn.commit()
    conn.close()
    return True


def check_user(username, password):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT password FROM login WHERE username = ?', (username,))
    row = cur.fetchone()

    if row:
        hashed_password = row[0]
        if sha256_crypt.verify(password, hashed_password):
            return True
    return False


@app.route("/")
def index():
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if register_user_to_db(username, password, confirm_password):
            flash('Registration successful', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_user(username, password):
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))
    else:
        return redirect(url_for('index'))


@app.route('/home', methods=['POST', "GET"])
def home():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    else:
        return "Invalid username or password!"


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)