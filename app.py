import sqlite3
from flask import Flask, flash, redirect, url_for, render_template, request, session
from passlib.hash import sha256_crypt


def register_user_to_db(username, password, confirm_password):
    if password != confirm_password:
        flash("Passwords don't match", 'error')
        return False  # Passwords do not match
    
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    hashed_password = sha256_crypt.encrypt(password)
    cur.execute('INSERT INTO login (username, password) VALUES (?, ?)', (username, hashed_password))
    con.commit()
    con.close()
    return True

def check_user(username, password):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('SELECT password FROM login WHERE username = ?', (username,))
    row = cur.fetchone()
    
    if row:
        hashed_password = row[0]
        if sha256_crypt.verify(password, hashed_password):
            return True
    return False


app = Flask(__name__)
app.secret_key = "r@nd0mSk_1"


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
        print(check_user(username, password))
        if check_user(username, password):
            session['username'] = username

        return redirect(url_for('home'))
    else:
        return redirect(url_for('index'))


@app.route('/home', methods=['POST', "GET"])
def home():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    else:
        return "Username or Password is wrong!"


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)