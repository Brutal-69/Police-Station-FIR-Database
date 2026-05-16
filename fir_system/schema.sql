CREATE DATABASE IF NOT EXISTS fir_db;
USE fir_db;

CREATE TABLE station (
    station_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    location VARCHAR(150),
    contact VARCHAR(20)
);

CREATE TABLE officer (
    officer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    `rank` VARCHAR(50),
    badge_number VARCHAR(20) UNIQUE,
    station_id INT,
    FOREIGN KEY (station_id) REFERENCES station(station_id)
);

CREATE TABLE complainant (
    complainant_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    cnic VARCHAR(15) UNIQUE,
    phone VARCHAR(20),
    address VARCHAR(200)
);

CREATE TABLE fir (
    fir_id INT AUTO_INCREMENT PRIMARY KEY,
    fir_number VARCHAR(30) UNIQUE,
    date_filed DATE,
    description TEXT,
    status ENUM('Open', 'Under Investigation', 'Closed', 'Dismissed'),
    complainant_id INT,
    officer_id INT,
    station_id INT,
    FOREIGN KEY (complainant_id) REFERENCES complainant(complainant_id),
    FOREIGN KEY (officer_id) REFERENCES officer(officer_id),
    FOREIGN KEY (station_id) REFERENCES station(station_id)
);

CREATE TABLE suspect (
    suspect_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    cnic VARCHAR(15),
    address VARCHAR(200),
    status ENUM('At Large', 'Arrested', 'Released', 'Convicted')
);

CREATE TABLE fir_suspect (
    fir_id INT,
    suspect_id INT,
    PRIMARY KEY (fir_id, suspect_id),
    FOREIGN KEY (fir_id) REFERENCES fir(fir_id),
    FOREIGN KEY (suspect_id) REFERENCES suspect(suspect_id)
);

CREATE TABLE evidence (
    evidence_id INT AUTO_INCREMENT PRIMARY KEY,
    fir_id INT,
    description VARCHAR(200),
    collected_date DATE,
    collected_by INT,
    FOREIGN KEY (fir_id) REFERENCES fir(fir_id),
    FOREIGN KEY (collected_by) REFERENCES officer(officer_id)
);

CREATE TABLE hearing (
    hearing_id INT AUTO_INCREMENT PRIMARY KEY,
    fir_id INT,
    hearing_date DATE,
    court_name VARCHAR(100),
    outcome VARCHAR(200),
    FOREIGN KEY (fir_id) REFERENCES fir(fir_id)
);

-- Sample Data
INSERT INTO station VALUES (1, 'Peshawar City Police Station', 'Qissa Khwani Bazaar, Peshawar', '091-1234567');
INSERT INTO station VALUES (2, 'Hayatabad Police Station', 'Phase 4, Hayatabad, Peshawar', '091-2345678');
INSERT INTO officer VALUES (1, 'Inspector Tariq Mehmood', 'Inspector', 'B-1001', 1);
INSERT INTO officer VALUES (2, 'DSP Khalid Afridi', 'DSP', 'B-1002', 1);
INSERT INTO officer VALUES (3, 'SI Rashid Khan', 'Sub-Inspector', 'B-2001', 2);