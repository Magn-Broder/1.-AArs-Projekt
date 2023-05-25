import sqlite3
from flask import Flask, flash, redirect, url_for, render_template, request, session

app = Flask(__name__)
app.secret_key = "r@nd0mSk_1"
DATABASE = 'database.db'


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_db_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS login (id INTEGER PRIMARY KEY AUTOINCREMENT, name, username TEXT, password TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS appointments (id INTEGER PRIMARY KEY AUTOINCREMENT, hairdresser TEXT, date TEXT, time TEXT, booked_by TEXT)')
    conn.commit()
    conn.close()


def register_user_to_db(name, username, password, confirm_password):
    if password != confirm_password:
        flash("Passwords er ikke ens", 'error')
        return False  # Passwords do not match

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO login (name, username, password) VALUES (?, ?, ?)', (name, username, password))
    conn.commit()
    conn.close()
    return True


def check_user(username, password):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT password FROM login WHERE username = ?', (username,))
    row = cur.fetchone()

    if row:
        stored_password = row[0]
        if stored_password == password:
            return True
    return False


def create_appointment(hairdresser, date, time):
    conn = get_db_connection()
    conn.execute('INSERT INTO appointments (hairdresser, date, time) VALUES (?, ?, ?)', (hairdresser, date, time))
    conn.commit()
    conn.close()


def book_appointment(appointment_id, booked_by):
    conn = get_db_connection()
    appointment = conn.execute('SELECT * FROM appointments WHERE id = ?', (appointment_id,)).fetchone()
    if appointment:
        if appointment['booked_by']:
            flash('Appointment already booked!', 'error')
        else:
            conn.execute('UPDATE appointments SET booked_by = ? WHERE id = ?', (booked_by, appointment_id))
            conn.commit()
            flash('Appointment booked successfully!', 'success')
    else:
        flash('Invalid appointment ID!', 'error')
    conn.close()


initialize_database()


@app.route("/")
def index():
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if register_user_to_db(name, username, password, confirm_password):
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

    return redirect(url_for('index'))


@app.route('/home', methods=['POST', "GET"])
def home():
    if 'username' in session:
        conn = get_db_connection()
        appointments = conn.execute('SELECT * FROM appointments WHERE date = date("now")').fetchall()
        conn.close()
        return render_template('home.html', username=session['username'], appointments=appointments)
    else:
        return "Brugernavn eller Password er forkert!"


@app.route('/create-appointment', methods=['GET', 'POST'])
def create_appointment():
    if request.method == 'POST':
        hairdresser = request.form['hairdresser']
        date = request.form['date']
        time = request.form['time']
        create_appointment(hairdresser, date, time)
        flash('Appointment created successfully!', 'success')
        return redirect(url_for('index'))

    if 'username' in session:
        username = session['username']
        conn = get_db_connection()
        user = conn.execute('SELECT name FROM login WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user:
            name = user['name']
            return render_template('create_appointment.html', name=name)

    return render_template('create_appointment.html')


@app.route('/book-appointment', methods=['GET', 'POST'])
def book_appointment():
    if request.method == 'POST':
        appointment_id = request.form['appointment_id']
        booked_by = request.form['booked_by']
        book_appointment(appointment_id, booked_by)
        return redirect(url_for('index'))

    conn = get_db_connection()
    appointments = conn.execute('SELECT * FROM appointments WHERE booked_by IS NULL').fetchall()
    conn.close()
    return render_template('book_appointment.html', appointments=appointments)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)