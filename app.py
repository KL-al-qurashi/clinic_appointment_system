# pip install -r requirements.txt    python app.py      http://127.0.0.1:5000       #

from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "change-this-secret-key-before-deployment"

DATABASE = "clinic.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('patient', 'doctor', 'admin')),
            phone TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            specialty TEXT NOT NULL,
            working_days TEXT NOT NULL,
            working_hours TEXT NOT NULL,
            room_number TEXT,
            bio TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            reason TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(patient_id) REFERENCES users(id),
            FOREIGN KEY(doctor_id) REFERENCES doctors(id)
        )
    """)

    conn.commit()
    seed_data(conn)
    conn.close()


def seed_data(conn):
    doctors_data = [
        {
            "name": "Dr. Ahmed Al-Harbi",
            "email": "ahmed@clinic.com",
            "password": "doctor123",
            "phone": "0551112233",
            "specialty": "General Medicine",
            "days": "Sunday - Thursday",
            "hours": "09:00 AM - 01:00 PM",
            "room": "Room 101",
            "bio": "General consultation, fever, flu, and common health conditions."
        },
        {
            "name": "Dr. Sara Al-Qahtani",
            "email": "sara@clinic.com",
            "password": "doctor123",
            "phone": "0552223344",
            "specialty": "Dentistry",
            "days": "Sunday - Wednesday",
            "hours": "10:00 AM - 03:00 PM",
            "room": "Room 203",
            "bio": "Dental checkups, cleaning, tooth pain, and oral health care."
        },
        {
            "name": "Dr. Khalid Al-Otaibi",
            "email": "khalid@clinic.com",
            "password": "doctor123",
            "phone": "0553334455",
            "specialty": "Pediatrics",
            "days": "Monday - Thursday",
            "hours": "01:00 PM - 06:00 PM",
            "room": "Room 305",
            "bio": "Child health care, vaccinations, and pediatric consultations."
        },
        {
            "name": "Dr. Noura Al-Zahrani",
            "email": "noura@clinic.com",
            "password": "doctor123",
            "phone": "0554445566",
            "specialty": "Dermatology",
            "days": "Sunday, Tuesday, Thursday",
            "hours": "11:00 AM - 04:00 PM",
            "room": "Room 210",
            "bio": "Skin conditions, acne, allergies, and dermatology consultation."
        },
        {
            "name": "Dr. Faisal Al-Ghamdi",
            "email": "faisal@clinic.com",
            "password": "doctor123",
            "phone": "0555556677",
            "specialty": "Cardiology",
            "days": "Monday - Wednesday",
            "hours": "08:00 AM - 12:00 PM",
            "room": "Room 401",
            "bio": "Heart health, blood pressure, and cardiac follow-up visits."
        }
    ]

    for doctor in doctors_data:
        existing_user = conn.execute(
            "SELECT id FROM users WHERE email = ?",
            (doctor["email"],)
        ).fetchone()

        if existing_user is None:
            cursor = conn.execute("""
                INSERT INTO users (full_name, email, password, role, phone)
                VALUES (?, ?, ?, 'doctor', ?)
            """, (
                doctor["name"],
                doctor["email"],
                generate_password_hash(doctor["password"]),
                doctor["phone"]
            ))
            user_id = cursor.lastrowid

            conn.execute("""
                INSERT INTO doctors 
                (user_id, specialty, working_days, working_hours, room_number, bio)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                doctor["specialty"],
                doctor["days"],
                doctor["hours"],
                doctor["room"],
                doctor["bio"]
            ))

    existing_patient = conn.execute(
        "SELECT id FROM users WHERE email = ?",
        ("patient@clinic.com",)
    ).fetchone()

    if existing_patient is None:
        conn.execute("""
            INSERT INTO users (full_name, email, password, role, phone)
            VALUES (?, ?, ?, 'patient', ?)
        """, (
            "Demo Patient",
            "patient@clinic.com",
            generate_password_hash("patient123"),
            "0550000000"
        ))

    conn.commit()


def login_required(role=None):
    def decorator(function):
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                flash("Please login first.", "warning")
                return redirect(url_for("login"))

            if role and session.get("role") != role:
                flash("You do not have permission to access this page.", "danger")
                return redirect(url_for("dashboard"))

            return function(*args, **kwargs)

        wrapper.__name__ = function.__name__
        return wrapper
    return decorator


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["full_name"] = user["full_name"]
            session["email"] = user["email"]
            session["role"] = user["role"]

            flash("Login successful.", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form["full_name"].strip()
        email = request.form["email"].strip().lower()
        phone = request.form["phone"].strip()
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("register"))

        conn = get_db_connection()
        existing_user = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()

        if existing_user:
            conn.close()
            flash("Email already exists. Please login.", "warning")
            return redirect(url_for("login"))

        conn.execute("""
            INSERT INTO users (full_name, email, password, role, phone)
            VALUES (?, ?, ?, 'patient', ?)
        """, (
            full_name,
            email,
            generate_password_hash(password),
            phone
        ))
        conn.commit()
        conn.close()

        flash("Account created successfully. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/dashboard")
@login_required()
def dashboard():
    if session["role"] == "doctor":
        return redirect(url_for("doctor_dashboard"))

    return redirect(url_for("patient_dashboard"))


@app.route("/patient/dashboard")
@login_required("patient")
def patient_dashboard():
    conn = get_db_connection()

    doctors = conn.execute("""
        SELECT doctors.*, users.full_name, users.email, users.phone
        FROM doctors
        JOIN users ON doctors.user_id = users.id
        ORDER BY users.full_name
    """).fetchall()

    appointments = conn.execute("""
        SELECT appointments.*, 
               users.full_name AS doctor_name,
               doctors.specialty
        FROM appointments
        JOIN doctors ON appointments.doctor_id = doctors.id
        JOIN users ON doctors.user_id = users.id
        WHERE appointments.patient_id = ?
        ORDER BY appointments.appointment_date DESC, appointments.appointment_time DESC
    """, (session["user_id"],)).fetchall()

    conn.close()

    return render_template(
        "patient_dashboard.html",
        doctors=doctors,
        appointments=appointments
    )


@app.route("/book/<int:doctor_id>", methods=["GET", "POST"])
@login_required("patient")
def book_appointment(doctor_id):
    conn = get_db_connection()

    doctor = conn.execute("""
        SELECT doctors.*, users.full_name, users.email, users.phone
        FROM doctors
        JOIN users ON doctors.user_id = users.id
        WHERE doctors.id = ?
    """, (doctor_id,)).fetchone()

    if doctor is None:
        conn.close()
        flash("Doctor not found.", "danger")
        return redirect(url_for("patient_dashboard"))

    if request.method == "POST":
        appointment_date = request.form["appointment_date"]
        appointment_time = request.form["appointment_time"]
        reason = request.form["reason"].strip()

        existing = conn.execute("""
            SELECT id FROM appointments
            WHERE doctor_id = ? 
            AND appointment_date = ?
            AND appointment_time = ?
            AND status != 'Cancelled'
        """, (doctor_id, appointment_date, appointment_time)).fetchone()

        if existing:
            conn.close()
            flash("This time slot is already booked. Please choose another time.", "warning")
            return redirect(url_for("book_appointment", doctor_id=doctor_id))

        conn.execute("""
            INSERT INTO appointments
            (patient_id, doctor_id, appointment_date, appointment_time, reason, status)
            VALUES (?, ?, ?, ?, ?, 'Pending')
        """, (
            session["user_id"],
            doctor_id,
            appointment_date,
            appointment_time,
            reason
        ))

        conn.commit()
        conn.close()

        flash("Appointment booked successfully.", "success")
        return redirect(url_for("patient_dashboard"))

    conn.close()
    return render_template("book_appointment.html", doctor=doctor)


@app.route("/doctor/dashboard")
@login_required("doctor")
def doctor_dashboard():
    conn = get_db_connection()

    doctor = conn.execute("""
        SELECT doctors.*
        FROM doctors
        WHERE doctors.user_id = ?
    """, (session["user_id"],)).fetchone()

    appointments = conn.execute("""
        SELECT appointments.*,
               users.full_name AS patient_name,
               users.phone AS patient_phone,
               users.email AS patient_email
        FROM appointments
        JOIN users ON appointments.patient_id = users.id
        WHERE appointments.doctor_id = ?
        ORDER BY appointments.appointment_date, appointments.appointment_time
    """, (doctor["id"],)).fetchall()

    stats = {
        "total": len(appointments),
        "pending": len([a for a in appointments if a["status"] == "Pending"]),
        "confirmed": len([a for a in appointments if a["status"] == "Confirmed"]),
        "cancelled": len([a for a in appointments if a["status"] == "Cancelled"])
    }

    conn.close()

    return render_template(
        "doctor_dashboard.html",
        appointments=appointments,
        stats=stats
    )


@app.route("/appointment/<int:appointment_id>/status", methods=["POST"])
@login_required("doctor")
def update_appointment_status(appointment_id):
    new_status = request.form["status"]

    if new_status not in ["Pending", "Confirmed", "Completed", "Cancelled"]:
        flash("Invalid status.", "danger")
        return redirect(url_for("doctor_dashboard"))

    conn = get_db_connection()

    doctor = conn.execute(
        "SELECT id FROM doctors WHERE user_id = ?",
        (session["user_id"],)
    ).fetchone()

    conn.execute("""
        UPDATE appointments
        SET status = ?
        WHERE id = ? AND doctor_id = ?
    """, (new_status, appointment_id, doctor["id"]))

    conn.commit()
    conn.close()

    flash("Appointment status updated.", "success")
    return redirect(url_for("doctor_dashboard"))


@app.route("/logout")
def logout():
    session.clear()
    flash("You have logged out successfully.", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
