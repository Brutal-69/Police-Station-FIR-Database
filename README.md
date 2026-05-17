Police Station FIR Management System

A web-based FIR (First Information Report) management system built for Peshawar Police, developed as a Database Systems course project at IMS Peshawar.

Tech Stack
- **Backend:** Python, Flask
- **Database:** MySQL
- **Frontend:** HTML, CSS (Jinja2 templates)

Features
- File and manage FIRs
- Track suspects and link them to cases
- Manage officer roster
- Record evidence and court hearings
- Filter and search FIR records
- Case status tracking (Open, Under Investigation, Closed, Dismissed)

Database
- 8 normalized tables (3NF)
- Tables: Station, Officer, Complainant, FIR, Suspect, FIR_Suspect, Evidence, Hearing

Setup
1. Import `schema.sql` into MySQL
2. Update DB credentials in `app1.py`
3. Install dependencies:
