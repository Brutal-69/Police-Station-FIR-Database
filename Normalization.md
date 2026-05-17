# Milestone 2 — Table Justification (FIR Database)

Station Table
Stores police station details like name, location, and contact. Each station has a unique ID.

Officer Table
Stores officer details and links each officer to a station.

Complainant Table
Stores FIR complainant information with unique CNIC.

FIR Table
Core table connecting complainant, officer, and station with FIR details.

Suspect Table
Stores suspect details and their case status.

FIR_Suspect Table
Handles many-to-many relationship between FIRs and suspects.

Evidence Table
Stores evidence linked to FIRs and collecting officers.

Hearing Table
Stores court hearing records for FIR cases.

Summary
Database is normalized to 3NF with no redundancy or transitive dependencies.