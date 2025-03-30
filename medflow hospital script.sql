CREATE DATABASE medflow;

USE medflow;


users-- Create the Users (Doctors) Table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(15) PRIMARY KEY,
    hospital_assigned VARCHAR(255) NOT NULL,
    national_id CHAR(8) UNIQUE NOT NULL,
    phone CHAR(10) UNIQUE NOT NULL,
    department VARCHAR(255) NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    residency VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the Patients Table
CREATE TABLE IF NOT EXISTS patients (
    id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    phone CHAR(10) UNIQUE NOT NULL,
    residency VARCHAR(255) NOT NULL,
    married BOOLEAN NOT NULL,
    spouse_name VARCHAR(255) NULL,
    age INT NOT NULL,
    gender VARCHAR(10) NOT NULL,
    ethnicity VARCHAR(50) NOT NULL CHECK (ethnicity IN ('Christian', 'Muslim', 'Pagan', 'Other')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE users
ADD COLUMN email VARCHAR(255) NOT NULL UNIQUE,
ADD COLUMN password VARCHAR(255) NOT NULL;
describe patients;
ALTER TABLE patients DROP PRIMARY KEY, ADD COLUMN patient_id VARCHAR(20) PRIMARY KEY FIRST;

-- 2. Outpatient Visits
CREATE TABLE outpatient_visits (
    visit_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id VARCHAR(20) NOT NULL,
    purpose VARCHAR(255) NOT NULL,
    visit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
);
-- 3. Triage Table
CREATE TABLE triage (
    triage_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id VARCHAR(20) NOT NULL,
    blood_pressure VARCHAR(10),
    heart_rate INT,
    temperature DECIMAL(4,1),
    weight DECIMAL(5,2),
    height DECIMAL(5,2),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
);

CREATE TABLE emergency_cases (
    case_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id VARCHAR(20) NOT NULL,
    emergency_condition TEXT NOT NULL, -- Renamed 'condition' to 'emergency_condition'
    admitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
);

CREATE TABLE consultations (
    consultation_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id VARCHAR(20) NOT NULL,
    user_id VARCHAR(15) NOT NULL,  -- Renamed from doctor_id to user_id to match users table
    notes TEXT NOT NULL,
    prescription TEXT,
    consultation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE  -- Reference users.id
);

-- 6. Maternity Table
CREATE TABLE maternity (
    maternity_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id VARCHAR(20) NOT NULL,
    delivery_date DATE,
    delivery_type ENUM('Normal', 'C-Section') NOT NULL,
    complications TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
);

-- 7. High Dependency Unit (HDU)
CREATE TABLE hdu (
    hdu_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id VARCHAR(20) NOT NULL,
    admission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    hdu_condition TEXT NOT NULL,
    monitoring_notes TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
);
-- 10. Medications Table
CREATE TABLE medications (
    medication_id INT AUTO_INCREMENT PRIMARY KEY,
    consultation_id INT NOT NULL,
    medicine_name VARCHAR(255) NOT NULL,
    dosage VARCHAR(100) NOT NULL,
    FOREIGN KEY (consultation_id) REFERENCES consultations(consultation_id) ON DELETE CASCADE
);

-- 11. Hospital Info Table (for dashboard statistics)
CREATE TABLE hospital_info (
    info_id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(255) NOT NULL,
    description TEXT NOT NULL
);
ALTER TABLE patients MODIFY id INT NULL;
ALTER TABLE patients DROP COLUMN id;

desc patients;
SHOW CREATE TABLE hdu;
INSERT INTO consultations (patient_id, user_id, notes, prescription)
VALUES ('PAT2025-0001', 'D12345', 'Test Notes', 'Test Prescription');

