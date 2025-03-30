# MedFlow Hospital Management System

## 📌 Project Overview
MedFlow is a web-based **hospital consultation system** designed to assist doctors in managing patient visits, tracking medical progress, and ensuring accurate AI-assisted medication prescriptions. The system integrates **Flask (Python) and MySQL** to provide a seamless hospital workflow.

## 🎯 Key Features
- **Patient Registration** – Store and manage patient details securely.
- **Outpatient Visit Management** – Track and manage OP visits with an initial consultation fee.
- **Triage & Diagnosis** – Record patient vitals and symptoms.
- **High Dependency Unit (HDU) Management** – Monitor critical patients in the HDU.
- **AI-Assisted Medication** – Utilize AI-powered analysis for TB diagnosis and treatment tracking.
- **User Authentication** – Secure login for doctors.

## 🏛️ Technologies Used
- **Backend**: Flask (Python)
- **Database**: MySQL
- **Frontend**: HTML, CSS, Bootstrap, JavaScript
- **Version Control**: Git & GitHub

## 📁 Project Structure
```
medflow-hospital/
│── static/                # CSS, JS, and images
│── templates/             # HTML templates (Flask Jinja2)
│── venv/                  # Virtual environment (excluded from Git)
│── app.py                 # Main Flask application
│── db.py                  # Database connection script
│── models.py              # Database models
│── requirements.txt       # Project dependencies
│── medflow.sql            # MySQL database schema and data
│── README.md              # Project documentation
│── .gitignore             # Files to exclude from Git
```

## 📌 Installation & Setup
### 1️⃣ Clone the Repository
```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/medflow-hospital.git
cd medflow-hospital
```

### 2️⃣ Set Up a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # For Mac/Linux
venv\Scripts\activate     # For Windows
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Set Up the MySQL Database
1. **Create a MySQL database:**
   ```sql
   CREATE DATABASE medflow;
   ```
2. **Import the database schema:**
   ```bash
   mysql -u root -p medflow < medflow.sql
   ```
3. **Update database credentials in `db.py`**

### 5️⃣ Run the Flask Application
```bash
flask run
```
Application will be available at: **http://127.0.0.1:5000**

## 📚 Team Members
This project is a **Software Engineering (II) group project** for the **Bachelor’s Degree program at St. Paul’s University (4th Year).**

- **BOBITNRB318722**
- **BOBITNRB394223**
- **BOBITNRB206523**

## 🎯 Future Enhancements
- AI-powered disease diagnosis and recommendation system
- Appointment scheduling
- Integration with external health data sources

## 📜 License
This project is for educational purposes under **St. Paul’s University** and is not intended for commercial use.

---
✅ **Developed for Software Engineering (II) | St. Paul’s University | 4th Year**
