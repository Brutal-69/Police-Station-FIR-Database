from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from datetime import date

app = Flask(__name__)
app.secret_key = 'fir_secret_key'

def get_db():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='Lmaoloogy@1',
        database='fir_db'
    )

# ---------- HOME ----------
@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) AS total FROM fir")
    total = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(*) AS open_firs FROM fir WHERE status='Open'")
    open_firs = cursor.fetchone()['open_firs']
    cursor.execute("SELECT COUNT(*) AS investigating FROM fir WHERE status='Under Investigation'")
    investigating = cursor.fetchone()['investigating']
    cursor.execute("SELECT COUNT(*) AS closed FROM fir WHERE status='Closed'")
    closed = cursor.fetchone()['closed']
    cursor.execute("""
        SELECT f.fir_id, f.fir_number, f.date_filed, f.status,
               c.name AS complainant, o.name AS officer
        FROM fir f
        JOIN complainant c ON f.complainant_id = c.complainant_id
        JOIN officer o ON f.officer_id = o.officer_id
        ORDER BY f.date_filed DESC LIMIT 5
    """)
    recent = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('index.html', total=total, open_firs=open_firs,
                           investigating=investigating, closed=closed, recent=recent)

# ---------- FIRs ----------
@app.route('/firs')
def firs():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    status_filter = request.args.get('status', '')
    search = request.args.get('search', '')
    query = """
        SELECT f.fir_id, f.fir_number, f.date_filed, f.status,
               c.name AS complainant, o.name AS officer, s.name AS station
        FROM fir f
        JOIN complainant c ON f.complainant_id = c.complainant_id
        JOIN officer o ON f.officer_id = o.officer_id
        JOIN station s ON f.station_id = s.station_id
        WHERE 1=1
    """
    params = []
    if status_filter:
        query += " AND f.status = %s"
        params.append(status_filter)
    if search:
        query += " AND (f.fir_number LIKE %s OR c.name LIKE %s)"
        params.extend([f'%{search}%', f'%{search}%'])
    query += " ORDER BY f.date_filed DESC"
    cursor.execute(query, params)
    fir_list = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('firs.html', firs=fir_list, status_filter=status_filter, search=search)

@app.route('/fir/new', methods=['GET', 'POST'])
def new_fir():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        fir_number = request.form['fir_number']
        description = request.form['description']
        status = request.form['status']
        date_filed = request.form['date_filed']
        # Complainant
        c_name = request.form['c_name']
        c_cnic = request.form['c_cnic']
        c_phone = request.form['c_phone']
        c_address = request.form['c_address']
        officer_id = request.form['officer_id']
        station_id = request.form['station_id']

        cursor.execute(
            "INSERT INTO complainant (name, cnic, phone, address) VALUES (%s, %s, %s, %s)",
            (c_name, c_cnic, c_phone, c_address)
        )
        complainant_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO fir (fir_number, date_filed, description, status, complainant_id, officer_id, station_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (fir_number, date_filed, description, status, complainant_id, officer_id, station_id)
        )
        db.commit()
        flash('FIR filed successfully!', 'success')
        cursor.close()
        db.close()
        return redirect(url_for('firs'))

    cursor.execute("SELECT * FROM officer")
    officers = cursor.fetchall()
    cursor.execute("SELECT * FROM station")
    stations = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('new_fir.html', officers=officers, stations=stations, today=date.today())

@app.route('/fir/<int:fir_id>')
def view_fir(fir_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT f.*, c.name AS complainant, c.cnic AS c_cnic, c.phone AS c_phone,
               c.address AS c_address, o.name AS officer, o.rank AS officer_rank,
               s.name AS station, s.location AS station_location
        FROM fir f
        JOIN complainant c ON f.complainant_id = c.complainant_id
        JOIN officer o ON f.officer_id = o.officer_id
        JOIN station s ON f.station_id = s.station_id
        WHERE f.fir_id = %s
    """, (fir_id,))
    fir = cursor.fetchone()
    cursor.execute("""
        SELECT su.* FROM suspect su
        JOIN fir_suspect fs ON su.suspect_id = fs.suspect_id
        WHERE fs.fir_id = %s
    """, (fir_id,))
    suspects = cursor.fetchall()
    cursor.execute("""
        SELECT e.*, o.name AS collected_by_name FROM evidence e
        JOIN officer o ON e.collected_by = o.officer_id
        WHERE e.fir_id = %s
    """, (fir_id,))
    evidence = cursor.fetchall()
    cursor.execute("SELECT * FROM hearing WHERE fir_id = %s ORDER BY hearing_date", (fir_id,))
    hearings = cursor.fetchall()
    cursor.execute("SELECT officer_id, name, `rank` FROM officer ORDER BY name")
    officers = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('view_fir.html', fir=fir, suspects=suspects, evidence=evidence, hearings=hearings, officers=officers)

@app.route('/fir/<int:fir_id>/update_status', methods=['POST'])
def update_status(fir_id):
    db = get_db()
    cursor = db.cursor()
    new_status = request.form['status']
    cursor.execute("UPDATE fir SET status = %s WHERE fir_id = %s", (new_status, fir_id))
    db.commit()
    cursor.close()
    db.close()
    flash('Status updated.', 'success')
    return redirect(url_for('view_fir', fir_id=fir_id))

# ---------- SUSPECTS ----------
@app.route('/suspects')
def suspects():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM suspect ORDER BY suspect_id DESC")
    suspect_list = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('suspects.html', suspects=suspect_list)

@app.route('/suspect/new', methods=['GET', 'POST'])
def new_suspect():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        name = request.form['name']
        cnic = request.form['cnic']
        address = request.form['address']
        status = request.form['status']
        fir_id = request.form['fir_id']
        cursor.execute(
            "INSERT INTO suspect (name, cnic, address, status) VALUES (%s, %s, %s, %s)",
            (name, cnic, address, status)
        )
        suspect_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO fir_suspect (fir_id, suspect_id) VALUES (%s, %s)",
            (fir_id, suspect_id)
        )
        db.commit()
        flash('Suspect added.', 'success')
        cursor.close()
        db.close()
        return redirect(url_for('suspects'))
    cursor.execute("SELECT fir_id, fir_number FROM fir")
    firs = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('new_suspect.html', firs=firs)

# ---------- OFFICERS ----------
@app.route('/officers')
def officers():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
    SELECT o.*, s.name AS station_name,
           COUNT(f.fir_id) AS fir_count
    FROM officer o
    JOIN station s ON o.station_id = s.station_id
    LEFT JOIN fir f ON o.officer_id = f.officer_id
    GROUP BY o.officer_id
    ORDER BY CASE o.rank
        WHEN 'DSP' THEN 1
        WHEN 'Inspector' THEN 2
        WHEN 'Sub-Inspector' THEN 3
        ELSE 4
    END
""")
    officer_list = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('officers.html', officers=officer_list)

# ---------- EVIDENCE ----------
@app.route('/fir/<int:fir_id>/add_evidence', methods=['POST'])
def add_evidence(fir_id):
    db = get_db()
    cursor = db.cursor()
    description = request.form['description']
    collected_date = request.form['collected_date']
    collected_by = request.form['collected_by']
    cursor.execute(
        "INSERT INTO evidence (fir_id, description, collected_date, collected_by) VALUES (%s, %s, %s, %s)",
        (fir_id, description, collected_date, collected_by)
    )
    db.commit()
    cursor.close()
    db.close()
    flash('Evidence added.', 'success')
    return redirect(url_for('view_fir', fir_id=fir_id))

# ---------- HEARINGS ----------
@app.route('/fir/<int:fir_id>/add_hearing', methods=['POST'])
def add_hearing(fir_id):
    db = get_db()
    cursor = db.cursor()
    hearing_date = request.form['hearing_date']
    court_name = request.form['court_name']
    outcome = request.form.get('outcome', '')
    cursor.execute(
        "INSERT INTO hearing (fir_id, hearing_date, court_name, outcome) VALUES (%s, %s, %s, %s)",
        (fir_id, hearing_date, court_name, outcome)
    )
    db.commit()
    cursor.close()
    db.close()
    flash('Hearing added.', 'success')
    return redirect(url_for('view_fir', fir_id=fir_id))

if __name__ == '__main__':
    app.run(debug=True)
