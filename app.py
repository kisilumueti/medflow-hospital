from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from config import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import re

app = Flask(__name__,template_folder="app/templates")

app.secret_key = "your_secret_key"  # Set a secret key for sessions

# Generate unique doctor ID
def generate_doctor_id():
    year = datetime.datetime.now().year % 100  # Get last two digits of the year
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")  # Corrected table name
    count = cursor.fetchone()[0] + 1  # Increment count
    conn.close()
    return f"doc{year}-{count:05d}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        hospital_assigned = request.form["hospital_assigned"]
        national_id = request.form["national_id"]
        phone = request.form["phone"]
        department = request.form["department"]
        residency = request.form["residency"]
        email = request.form["email"]
        password = request.form["password"]

        # Validate input
        if not (national_id.isdigit() and len(national_id) == 8):
            flash("National ID must be 8 digits.", "danger")
            return redirect(url_for("register"))
        
        if not (phone.isdigit() and len(phone) == 10):
            flash("Phone number must be 10 digits.", "danger")
            return redirect(url_for("register"))

        doctor_id = generate_doctor_id()
        hashed_password = generate_password_hash(password)  # Hash password

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (id, hospital_assigned, national_id, phone, department, first_name, last_name, residency, email, password)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (doctor_id, hospital_assigned, national_id, phone, department, first_name, last_name, residency, email, hashed_password))
            conn.commit()
            conn.close()
            flash("Registration successful!", "success")
            return redirect(url_for("login"))
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "danger")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Check if the email exists
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if not user:
                flash("Email not found!", "danger")
            elif not check_password_hash(user['password'], password):
                flash("Incorrect password!", "danger")
            else:
                # Start session and store user details
                session["user_id"] = user["id"]  # Store the unique user ID
                session["user_name"] = f"{user['first_name']} {user['last_name']}"  # Store full name
                session["department"] = user["department"]  # Store department if needed

                flash("Login successful!", "success")
                return redirect(url_for("dashboard"))  # Redirect to dashboard

        except Exception as e:
            flash(f"Database error: {e}", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template("login.html")


@app.route("/reset", methods=["GET", "POST"])
def reset():
    if request.method == "POST":
        email = request.form["email"]

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if user:
                session["reset_email"] = email  # Store email in session for next step
                return redirect(url_for("reset_password"))  # Redirect to the password reset form
            else:
                flash("Email not found!", "danger")
        except Exception as e:
            flash(f"Error: {e}", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template("reset.html")

@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if "reset_email" not in session:
        flash("Session expired. Please try again.", "danger")
        return redirect(url_for("reset"))

    if request.method == "POST":
        new_password = request.form["new_password"]
        email = session["reset_email"]
        hashed_password = generate_password_hash(new_password)  # Hash new password

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password, email))
            conn.commit()

            flash("Password successfully reset! You can now log in.", "success")
            session.pop("reset_email", None)  # Remove from session
            return redirect(url_for("login"))

        except Exception as e:
            flash(f"Error: {e}", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template("reset_password.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for("login"))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT COUNT(*) AS total_doctors FROM users WHERE department != 'Admin'")
    total_doctors = cursor.fetchone()["total_doctors"]
    
    cursor.execute("SELECT COUNT(*) AS total_patients FROM patients")
    total_patients = cursor.fetchone()["total_patients"]
    
    cursor.execute("SELECT COUNT(*) AS total_outpatient_visits FROM outpatient_visits")
    total_outpatient_visits = cursor.fetchone()["total_outpatient_visits"]
    
    cursor.close()
    conn.close()
    
    return render_template("dashboard.html", total_doctors=total_doctors, total_patients=total_patients, total_outpatient_visits=total_outpatient_visits)



def generate_patient_id():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch the latest patient_id
    cursor.execute("SELECT patient_id FROM patients ORDER BY created_at DESC LIMIT 1")
    last_patient = cursor.fetchone()
    
    year = datetime.datetime.now().year

    if last_patient:
        # Extract the numeric part of the last patient_id
        match = re.search(r"PAT(\d+)-(\d+)", last_patient[0])
        if match and int(match.group(1)) == year:
            count = int(match.group(2)) + 1
        else:
            count = 1  # Reset count for new year
    else:
        count = 1  # First patient in the system

    cursor.close()
    conn.close()

    return f"PAT{year}-{count:04d}"

@app.route("/register_patient", methods=["GET", "POST"])
def register_patient():
    patient_id = generate_patient_id()  # Generate a new Patient ID

    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        phone = request.form["phone"]
        residency = request.form["residency"]
        married = int(request.form["married"])
        spouse_name = request.form.get("spouse_name", None)
        age = int(request.form["age"])
        gender = request.form["gender"]
        ethnicity = request.form["ethnicity"]

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO patients (patient_id, first_name, last_name, phone, residency, married, spouse_name, age, gender, ethnicity)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (patient_id, first_name, last_name, phone, residency, married, spouse_name, age, gender, ethnicity))
            conn.commit()
            flash("Patient registered successfully!", "success")
        except Exception as e:
            flash(f"Error: {e}", "danger")
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for("dashboard"))  # Redirect to dashboard after registration

    return render_template("register_patient.html", patient_id=patient_id)  # Pass patient_id to the template

@app.route("/outpatient", methods=["GET", "POST"])
def outpatient():
    if request.method == "POST":
        patient_id = request.form["patient_id"]
        purpose = request.form["purpose"]
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO outpatient_visits (patient_id, purpose) VALUES (%s, %s)", (patient_id, purpose))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Outpatient visit recorded!", "success")
        
    return render_template("outpatient.html")

@app.route("/triage", methods=["GET", "POST"])
def triage():
    if request.method == "POST":
        patient_id = request.form["patient_id"]
        blood_pressure = request.form["blood_pressure"]
        heart_rate = request.form["heart_rate"]
        temperature = request.form["temperature"]
        weight = request.form["weight"]
        height = request.form["height"]
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO triage (patient_id, blood_pressure, heart_rate, temperature, weight, height) VALUES (%s, %s, %s, %s, %s, %s)", (patient_id, blood_pressure, heart_rate, temperature, weight, height))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Triage details recorded!", "success")
        
    return render_template("triage.html")

@app.route("/emergency", methods=["GET", "POST"])
def emergency():
    if request.method == "POST":
        patient_id = request.form["patient_id"]
        emergency_condition = request.form["emergency_condition"]
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO emergency_cases (patient_id, emergency_condition) VALUES (%s, %s)", (patient_id, emergency_condition))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Emergency case recorded!", "success")
        
    return render_template("emergency.html")

@app.route("/consultation", methods=["GET", "POST"])
def consultation():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # Fetch rows as dictionaries
    patient_details = None
    triage_details = None
    doctors = []

    if request.method == "POST":
        patient_id = request.form.get("patient_id", "").strip()

        # Verify that patient_id exists in the patients table
        cursor.execute("SELECT patient_id, first_name, last_name, age, gender FROM patients WHERE patient_id = %s", (patient_id,))
        patient_details = cursor.fetchone()

        if not patient_details:
            flash("Error: Patient ID does not exist!", "danger")
            return redirect(url_for("consultation"))

        # Fetch triage details
        cursor.execute("SELECT triage_id, patient_id, blood_pressure, heart_rate, temperature, weight, height FROM triage WHERE patient_id = %s", (patient_id,))
        triage_details = cursor.fetchone()

        # Fetch doctors from users table
        cursor.execute("SELECT id, first_name, last_name FROM users WHERE department = 'Doctor'")
        doctors = cursor.fetchall()

        # If form has consultation details
        if "doctor_id" in request.form and "notes" in request.form:
            doctor_id = request.form.get("doctor_id", "").strip()
            notes = request.form.get("notes", "").strip()
            prescription = request.form.get("prescription", None)

            # Ensure doctor_id is valid
            cursor.execute("SELECT id FROM users WHERE id = %s AND department = 'Doctor'", (doctor_id,))
            doctor_exists = cursor.fetchone()
            if not doctor_exists:
                flash("Error: Selected doctor does not exist!", "danger")
                return redirect(url_for("consultation"))

            # Insert into consultations table
            cursor.execute("""
                INSERT INTO consultations (patient_id, user_id, notes, prescription)
                VALUES (%s, %s, %s, %s)
            """, (patient_id, doctor_id, notes, prescription))

            conn.commit()
            flash("Consultation details recorded successfully!", "success")

    cursor.close()
    conn.close()
    return render_template("consultation.html", patient=patient_details, triage=triage_details, doctors=doctors)

@app.route("/maternity", methods=["GET", "POST"])
def maternity():
    if request.method == "POST":
        patient_id = request.form["patient_id"]
        delivery_date = request.form["delivery_date"]
        delivery_type = request.form["delivery_type"]
        complications = request.form["complications"]
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO maternity (patient_id, delivery_date, delivery_type, complications) VALUES (%s, %s, %s, %s)", (patient_id, delivery_date, delivery_type, complications))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Maternity details recorded!", "success")
        
    return render_template("maternity.html")

@app.route("/hdu", methods=["GET", "POST"])
def hdu():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch all patients for dropdown selection
    cursor.execute("SELECT patient_id, first_name, last_name FROM patients")
    patients = cursor.fetchall()
    
    if request.method == "POST":
        patient_id = request.form.get("patient_id")
        hdu_condition = request.form.get("hdu_condition")  # Ensure correct naming
        monitoring_notes = request.form.get("monitoring_notes")
        
        if not patient_id or not hdu_condition:
            flash("Patient selection and condition are required!", "danger")
        else:
            cursor.execute(
                "INSERT INTO hdu (patient_id, hdu_condition, monitoring_notes) VALUES (%s, %s, %s)",
                (patient_id, hdu_condition, monitoring_notes)
            )
            conn.commit()
            flash("HDU details recorded!", "success")
    
    cursor.close()
    conn.close()
    
    return render_template("hdu.html", patients=patients)


@app.route("/medications", methods=["GET", "POST"])
def medications():
    if request.method == "POST":
        consultation_id = request.form["consultation_id"]
        medicine_name = request.form["medicine_name"]
        dosage = request.form["dosage"]
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO medications (consultation_id, medicine_name, dosage) VALUES (%s, %s, %s)", (consultation_id, medicine_name, dosage))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Medication details recorded!", "success")
        
    return render_template("medications.html")

if __name__ == "__main__":
    app.run(debug=True)
