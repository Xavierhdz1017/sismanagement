from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database initialization
def init_db():
    with sqlite3.connect('students.db') as conn:
        c = conn.cursor()

        # Students Table (Updated)
        c.execute('''CREATE TABLE IF NOT EXISTS students (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT NOT NULL,
                        phone TEXT NOT NULL,
                        gender TEXT,
                        dob TEXT,
                        address TEXT,
                        demographics TEXT,
                        guardian_contact TEXT,
                        ssn TEXT,
                        badge TEXT,
                        image_path TEXT)''')

        # Attendance Table (Updated)
        c.execute('''CREATE TABLE IF NOT EXISTS attendance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id INTEGER,
                        date TEXT,
                        time_in TEXT,
                        time_out TEXT,
                        breaks INTEGER,
                        total_hours REAL,
                        status TEXT,
                        FOREIGN KEY (student_id) REFERENCES students (id))''')

        # Grades Table
        c.execute('''CREATE TABLE IF NOT EXISTS grades (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id INTEGER,
                        subject TEXT,
                        assignment TEXT,
                        grade TEXT,
                        date TEXT,
                        FOREIGN KEY (student_id) REFERENCES students (id))''')

        # Schedule Table
        c.execute('''CREATE TABLE IF NOT EXISTS schedule (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id INTEGER,
                        class_name TEXT,
                        day TEXT,
                        time TEXT,
                        location TEXT,
                        FOREIGN KEY (student_id) REFERENCES students (id))''')

        # Ledger Table
        c.execute('''CREATE TABLE IF NOT EXISTS ledger (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id INTEGER,
                        entry_date TEXT,
                        description TEXT,
                        method TEXT,
                        charges REAL,
                        payments REAL,
                        balance REAL,
                        FOREIGN KEY (student_id) REFERENCES students (id))''')

        conn.commit()

init_db()

# Route to display the homepage
@app.route('/')
def index():
    return render_template('index.html')

# Route to display and add students
@app.route('/students', methods=['GET', 'POST'])
def students():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        gender = request.form.get('gender', 'Not specified')
        dob = request.form.get('dob', '')
        address = request.form.get('address', '')
        demographics = request.form.get('demographics', '')
        guardian_contact = request.form.get('guardian_contact', '')
        ssn = request.form.get('ssn', '')
        badge = request.form.get('badge', '')
        image = request.files.get('image')

        image_path = None
        if image and image.filename:
            image_filename = image.filename
            image_path = os.path.join('uploads', image_filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        try:
            with sqlite3.connect('students.db') as conn:
                c = conn.cursor()
                c.execute('''INSERT INTO students 
                             (name, email, phone, gender, dob, address, demographics, guardian_contact, ssn, badge, image_path) 
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                          (name, email, phone, gender, dob, address, demographics, guardian_contact, ssn, badge, image_path))
                conn.commit()
                flash('Student added successfully!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')

    with sqlite3.connect('students.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM students")
        students = c.fetchall()

    return render_template('students.html', students=students)

# Route to record attendance
@app.route('/record_attendance/<int:student_id>', methods=['GET', 'POST'])
def record_attendance(student_id):
    with sqlite3.connect('students.db') as conn:
        c = conn.cursor()
        c.execute("SELECT name FROM students WHERE id=?", (student_id,))
        student = c.fetchone()

        if not student:
            flash('Student not found!', 'danger')
            return redirect(url_for('students'))

        if request.method == 'POST':
            date = request.form['date']
            time_in = request.form['time_in']
            time_out = request.form['time_out']
            breaks = int(request.form['breaks'])
            status = request.form['status']

            # Calculate total hours
            time_in_dt = datetime.strptime(time_in, '%H:%M')
            time_out_dt = datetime.strptime(time_out, '%H:%M')
            total_hours = (time_out_dt - time_in_dt).seconds / 3600 - (breaks / 60)

            try:
                c.execute('''INSERT INTO attendance 
                             (student_id, date, time_in, time_out, breaks, total_hours, status) 
                             VALUES (?, ?, ?, ?, ?, ?, ?)''',
                          (student_id, date, time_in, time_out, breaks, total_hours, status))
                conn.commit()
                flash('Attendance recorded successfully!', 'success')
                return redirect(url_for('students'))
            except Exception as e:
                flash(f'Error: {str(e)}', 'danger')

    return render_template('record_attendance.html', student=student)

# Additional routes for grades, schedules, and ledger can be added similarly

if __name__ == '__main__':
    app.run(debug=True, port=5002)
