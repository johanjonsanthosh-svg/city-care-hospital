from flask import Flask, request, redirect, url_for, session, render_template_string, flash
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = "city-care-hospital-school-project"

# ==============================================================
# CITY CARE HOSPITAL - WEB VERSION
# Same core hospital data/features as the GUI project.
# Data is kept in memory for a school-project demo.
# ==============================================================

patients = []
appointments = []
prescriptions = []
bills = []

patient_counter = 1001
online_booking_counter = 1
hospital_token_counter = 1

doctors = [
    {"id": "D101", "name": "Dr. Arjun Menon", "department": "Cardiology"},
    {"id": "D102", "name": "Dr. Sarah Thomas", "department": "Pediatrics"},
    {"id": "D103", "name": "Dr. Rahul Nair", "department": "Orthopedics"},
    {"id": "D104", "name": "Dr. Meera Joseph", "department": "Dermatology"},
    {"id": "D105", "name": "Dr. Daniel Mathew", "department": "General Medicine"},
    {"id": "D106", "name": "Dr. Ananya Sharma", "department": "Gynecology"},
    {"id": "D107", "name": "Dr. Faisal Ahmed", "department": "ENT"},
    {"id": "D108", "name": "Dr. Neha Kapoor", "department": "Ophthalmology"},
    {"id": "D109", "name": "Dr. Joseph George", "department": "General Surgery"}
]

receptionists = [
    {"id": "R001", "name": "Reception Desk 1"},
    {"id": "R002", "name": "Reception Desk 2"},
    {"id": "R003", "name": "Reception Desk 3"}
]

CSS = """
:root{
    --navy:#12304a; --blue:#1769aa; --blue2:#0e5a94;
    --bg:#f4f7fb; --card:#fff; --muted:#6c7b88;
    --border:#dce6ed; --soft:#eef5fa; --danger:#b42318;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:#243447;font-family:Inter,Segoe UI,Arial,sans-serif}
a{text-decoration:none;color:inherit}
.topbar{height:72px;background:#fff;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;padding:0 5%;position:sticky;top:0;z-index:5}
.brand{display:flex;align-items:center;gap:12px}
.logo{width:42px;height:42px;border-radius:12px;background:var(--blue);color:#fff;display:grid;place-items:center;font-weight:800;font-size:21px}
.brand strong{font-size:18px;color:var(--navy)} .brand span{display:block;font-size:12px;color:var(--muted);margin-top:2px}
.container{width:min(1120px,92%);margin:0 auto;padding:38px 0 55px}
.hero{padding:18px 0 28px}.hero h1{margin:0;color:var(--navy);font-size:36px}.hero p{color:var(--muted);font-size:15px}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.card{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:24px;box-shadow:0 5px 18px rgba(18,48,74,.04)}
.card h3{margin:0 0 8px;color:var(--navy)} .card p{color:var(--muted);line-height:1.55}
.btn{display:inline-block;border:0;border-radius:10px;padding:11px 16px;font-weight:700;cursor:pointer;font-size:14px;background:#eaf1f7;color:var(--navy)}
.btn.primary{background:var(--blue);color:#fff}.btn.primary:hover{background:var(--blue2)}
.btn.danger{background:#fff0ee;color:var(--danger)}
.actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}
.header{display:flex;justify-content:space-between;align-items:flex-start;gap:20px;margin-bottom:22px}
.header h1{margin:0;color:var(--navy);font-size:28px}.header p{margin:7px 0;color:var(--muted)}
.form-card{max-width:760px;margin:auto}.field{margin-bottom:15px}.field label{display:block;font-weight:700;font-size:13px;color:#405261;margin-bottom:7px}
input,select,textarea{width:100%;padding:12px;border:1px solid #cbd8e1;border-radius:10px;background:#fff;font:inherit;outline:none}
input:focus,select:focus,textarea:focus{border-color:var(--blue);box-shadow:0 0 0 3px rgba(23,105,170,.10)}
.two{display:grid;grid-template-columns:1fr 1fr;gap:15px}
table{width:100%;border-collapse:collapse;background:#fff;border:1px solid var(--border);border-radius:14px;overflow:hidden}
th,td{text-align:left;padding:13px 14px;border-bottom:1px solid #e7edf2;font-size:13px}
th{background:#eaf1f7;color:#173b56}tr:last-child td{border-bottom:0}
.alert{padding:13px 15px;border-radius:10px;margin-bottom:16px;background:#fff5d8;color:#755b00;border:1px solid #f0dc9b}
.flash{padding:13px 15px;border-radius:10px;margin-bottom:16px;background:#e8f5ec;color:#17603a;border:1px solid #b9dfc7}
.empty{padding:45px;text-align:center;background:#fff;border:1px dashed var(--border);border-radius:15px;color:var(--muted)}
.kpi{font-size:30px;font-weight:800;color:var(--navy);margin-top:8px}
.pill{display:inline-block;padding:5px 9px;border-radius:999px;background:#eaf1f7;color:#245778;font-size:12px;font-weight:700}
.bill-total{font-size:25px;font-weight:800;color:var(--navy);text-align:right}
.footer{text-align:center;color:#8a98a4;font-size:12px;padding:20px}
@media(max-width:800px){.grid{grid-template-columns:1fr 1fr}.two{grid-template-columns:1fr}.topbar{padding:0 4%}}
@media(max-width:540px){.grid{grid-template-columns:1fr}.hero h1{font-size:29px}.container{padding-top:25px}table{display:block;overflow:auto;white-space:nowrap}}
"""

BASE = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ title }} | City Care Hospital</title>
<style>{{ css }}</style>
</head>
<body>
<header class="topbar">
  <a class="brand" href="{{ url_for('home') }}">
    <div class="logo">+</div>
    <div><strong>City Care Hospital</strong><span>Healthcare Management System</span></div>
  </a>
  <div class="actions" style="margin:0">
    {% if session.get('role') %}
      <a class="btn" href="{{ url_for('home') }}">Home</a>
      <a class="btn danger" href="{{ url_for('logout') }}">Logout</a>
    {% endif %}
  </div>
</header>
<main class="container">
{% with messages = get_flashed_messages() %}
  {% for message in messages %}<div class="flash">{{ message }}</div>{% endfor %}
{% endwith %}
{{ content|safe }}
</main>
<footer class="footer">City Care Hospital </footer>
</body>
</html>
"""

def page(title, body, **ctx):
    content = render_template_string(body, **ctx)
    return render_template_string(BASE, title=title, css=CSS, content=content)

def role_required(role):
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if session.get("role") != role:
                flash("Please log in to continue.")
                return redirect(url_for("home"))
            return fn(*args, **kwargs)
        return wrapper
    return deco

def find_patient(name, phone):
    for p in patients:
        if p["name"].strip().lower() == name.strip().lower() and p["phone"].strip() == phone.strip():
            return p
    return None

def find_doctor(doctor_id):
    return next((d for d in doctors if d["id"] == doctor_id), None)

# ==============================================================
# HOME / GENERAL
# ==============================================================

@app.route("/")
def home():
    body = """
    <div class="hero">
      <h1>City Care Hospital</h1>
      <p>A simple hospital management system with separate patient, doctor and receptionist portals.</p>
    </div>
    <div class="grid">
      <div class="card"><h3>Patient Portal</h3><p>View doctors and departments, book appointments, check appointments, prescriptions and bills.</p>
        <div class="actions"><a class="btn primary" href="{{ url_for('patient_portal') }}">Open Patient Portal</a></div>
      </div>
      <div class="card"><h3>Doctor Portal</h3><p>Access doctor appointments, assigned patients and prescription tools.</p>
        <div class="actions"><a class="btn primary" href="{{ url_for('doctor_login') }}">Doctor Login</a></div>
      </div>
      <div class="card"><h3>Receptionist Portal</h3><p>Check in online bookings, register walk-ins, manage records, appointments and bills.</p>
        <div class="actions"><a class="btn primary" href="{{ url_for('receptionist_login') }}">Receptionist Login</a></div>
      </div>
      <div class="card"><h3>Doctors</h3><p>Browse the hospital doctor directory.</p>
        <div class="actions"><a class="btn" href="{{ url_for('doctors_page') }}">View Doctors</a></div>
      </div>
      <div class="card"><h3>Departments</h3><p>See the departments available at City Care Hospital.</p>
        <div class="actions"><a class="btn" href="{{ url_for('departments_page') }}">View Departments</a></div>
      </div>
      <div class="card"><h3>Close App</h3><p>A website cannot reliably close your browser tab because of browser security. Close the tab/window normally when finished.</p>
      </div>
    </div>
    """
    return page("Home", body)

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for("home"))

@app.route("/doctors")
def doctors_page():
    from_portal = request.args.get("from", "").lower()
    back_url = url_for("patient_portal") if from_portal == "patient" else url_for("home")
    back_label = "Back to Patient Portal" if from_portal == "patient" else "Back Home"
    body = """
    <div class="header"><div><h1>Doctor Directory</h1><p>Doctors available at City Care Hospital.</p></div><a class="btn" href="{{ back_url }}">{{ back_label }}</a></div>
    <div class="card"><table><tr><th>ID</th><th>Doctor</th><th>Department</th></tr>
    {% for d in doctors %}<tr><td>{{ d.id }}</td><td>{{ d.name }}</td><td><span class="pill">{{ d.department }}</span></td></tr>{% endfor %}
    </table></div>
    """
    return page("Doctors", body, doctors=doctors, back_url=back_url, back_label=back_label)

@app.route("/departments")
def departments_page():
    from_portal = request.args.get("from", "").lower()
    back_url = url_for("patient_portal") if from_portal == "patient" else url_for("home")
    back_label = "Back to Patient Portal" if from_portal == "patient" else "Back Home"
    departments = []
    for d in doctors:
        if d["department"] not in departments:
            departments.append(d["department"])
    body = """
    <div class="header"><div><h1>Departments</h1><p>Hospital departments and their doctors.</p></div><a class="btn" href="{{ back_url }}">{{ back_label }}</a></div>
    <div class="grid">
    {% for dep in departments %}
      <div class="card"><h3>{{ dep }}</h3>
      {% for d in doctors if d.department == dep %}<p style="margin:5px 0">{{ d.name }} <span class="pill">{{ d.id }}</span></p>{% endfor %}
      </div>
    {% endfor %}
    </div>
    """
    return page("Departments", body, departments=departments, doctors=doctors, back_url=back_url, back_label=back_label)

# ==============================================================
# PATIENT PORTAL
# ==============================================================

@app.route("/patient")
def patient_portal():
    body = """
    <div class="hero"><h1>Patient Portal</h1><p>Choose a patient service.</p></div>
    <div class="grid">
      <div class="card"><h3>View Doctors</h3><p>Browse available doctors and departments.</p><a class="btn" href="{{ url_for('doctors_page', from='patient') }}">Open</a></div>
      <div class="card"><h3>View Departments</h3><p>See hospital departments.</p><a class="btn" href="{{ url_for('departments_page', from='patient') }}">Open</a></div>
      <div class="card"><h3>Book Appointment</h3><p>Create an online appointment and receive a booking number.</p><a class="btn primary" href="{{ url_for('book_appointment') }}">Book</a></div>
      <div class="card"><h3>My Appointments</h3><p>Find appointments using your name and phone number.</p><a class="btn" href="{{ url_for('patient_appointments') }}">View</a></div>
      <div class="card"><h3>My Profile</h3><p>View a registered patient profile.</p><a class="btn" href="{{ url_for('patient_profile') }}">View</a></div>
      <div class="card"><h3>My Prescription</h3><p>View prescriptions issued by a doctor.</p><a class="btn" href="{{ url_for('patient_prescription') }}">View</a></div>
      <div class="card"><h3>Cash Bill</h3><p>View your generated hospital bill.</p><a class="btn" href="{{ url_for('patient_bill') }}">View</a></div>
    </div>
    """
    return page("Patient Portal", body)

@app.route("/patient/book", methods=["GET","POST"])
def book_appointment():
    global patient_counter, online_booking_counter
    if request.method == "POST":
        data = {k: request.form.get(k, "").strip() for k in ["doctor_id","name","age","gender","phone","email","date","time"]}
        if not all(data.values()):
            flash("Please complete every appointment field.")
            return redirect(url_for("book_appointment"))
        if not data["age"].isdigit():
            flash("Age must be entered as a number.")
            return redirect(url_for("book_appointment"))
        doctor = find_doctor(data["doctor_id"])
        if not doctor:
            flash("Invalid doctor selection.")
            return redirect(url_for("book_appointment"))

        patient_id = "P" + str(patient_counter); patient_counter += 1
        patient = {"id":patient_id,"name":data["name"],"age":data["age"],"gender":data["gender"],"phone":data["phone"],"email":data["email"]}
        patients.append(patient)

        online_number = "O" + str(online_booking_counter).zfill(3); online_booking_counter += 1
        appointment = {
            "online_number":online_number,"patient_id":patient["id"],"patient_name":patient["name"],
            "phone":patient["phone"],"age":patient["age"],"gender":patient["gender"],"email":patient["email"],
            "doctor_id":doctor["id"],"doctor_name":doctor["name"],"department":doctor["department"],
            "date":data["date"],"time":data["time"],"hospital_token":""
        }
        appointments.append(appointment)
        return redirect(url_for("booking_confirmation", number=online_number))

    body = """
    <div class="header"><div><h1>Book Appointment</h1><p>Complete the form and press BOOK APPOINTMENT.</p></div><a class="btn" href="{{ url_for('patient_portal') }}">Back to Patient Portal</a></div>
    <div class="card form-card"><form method="post">
      <div class="field"><label>Doctor</label><select name="doctor_id" required><option value="">Select doctor</option>{% for d in doctors %}<option value="{{d.id}}">{{d.id}} - {{d.name}} - {{d.department}}</option>{% endfor %}</select></div>
      <div class="field"><label>Full Name</label><input name="name" required></div>
      <div class="two">
        <div class="field"><label>Age</label><input name="age" type="number" min="0" required></div>
        <div class="field"><label>Gender</label><select name="gender" required><option value="">Select</option><option>Male</option><option>Female</option><option>Other</option></select></div>
      </div>
      <div class="two">
        <div class="field"><label>Contact Number</label><input name="phone" required></div>
        <div class="field"><label>Email Address</label><input name="email" type="email" required></div>
      </div>
      <div class="two">
        <div class="field"><label>Appointment Date</label><input name="date" value="{{ today }}" required></div>
        <div class="field"><label>Appointment Time</label><input name="time" placeholder="10:30 AM" required></div>
      </div>
      <div class="actions"><button class="btn primary" type="submit">BOOK APPOINTMENT</button><button class="btn" type="reset">CLEAR FORM</button></div>
    </form></div>
    """
    return page("Book Appointment", body, doctors=doctors, today=datetime.now().strftime("%d/%m/%Y"))

@app.route("/patient/booking/<number>")
def booking_confirmation(number):
    appointment = next((a for a in appointments if a["online_number"] == number), None)
    if not appointment: return redirect(url_for("patient_portal"))
    body = """
    <div class="header"><div><h1>Appointment Confirmed</h1><p>Your online booking has been saved.</p></div></div>
    <div class="card">
      <h3>Booking Details</h3>
      <p><b>Patient:</b> {{ a.patient_name }}</p><p><b>Patient ID:</b> {{ a.patient_id }}</p>
      <p><b>Online Booking No.:</b> <span class="pill">{{ a.online_number }}</span></p>
      <p><b>Doctor:</b> {{ a.doctor_name }}</p><p><b>Department:</b> {{ a.department }}</p>
      <p><b>Date:</b> {{ a.date }}</p><p><b>Time:</b> {{ a.time }}</p>
      <div class="actions"><a class="btn primary" href="{{ url_for('patient_portal') }}">Back to Patient Portal</a></div>
    </div>
    """
    return page("Booking Confirmed", body, a=appointment)

def identity_form(action, title, description):
    body = """
    <div class="header"><div><h1>{{ title }}</h1><p>{{ description }}</p></div><a class="btn" href="{{ url_for('patient_portal') }}">Back to Patient Portal</a></div>
    <div class="card form-card"><form method="post" action="{{ action }}">
      <div class="field"><label>Patient Name</label><input name="name" required></div>
      <div class="field"><label>Phone Number</label><input name="phone" required></div>
      <button class="btn primary" type="submit">SEARCH</button>
    </form></div>
    """
    return page(title, body, action=action, description=description)

@app.route("/patient/appointments", methods=["GET","POST"])
def patient_appointments():
    if request.method == "POST":
        name, phone = request.form.get("name","").strip(), request.form.get("phone","").strip()
        found = [a for a in appointments if a["patient_name"].lower()==name.lower() and a["phone"]==phone]
        if not found:
            flash("No appointments found for that patient.")
            return redirect(url_for("patient_appointments"))
        body = """
        <div class="header"><div><h1>My Appointments</h1><p>Appointments for {{ name }}.</p></div><a class="btn" href="{{ url_for('patient_portal') }}">Back to Patient Portal</a></div>
        <div class="card"><table><tr><th>Online No.</th><th>Token</th><th>Doctor</th><th>Department</th><th>Date</th><th>Time</th></tr>
        {% for a in found %}<tr><td>{{a.online_number}}</td><td>{{a.hospital_token or 'Pending'}}</td><td>{{a.doctor_name}}</td><td>{{a.department}}</td><td>{{a.date}}</td><td>{{a.time}}</td></tr>{% endfor %}
        </table></div>
        """
        return page("My Appointments", body, found=found, name=name)
    return identity_form(url_for("patient_appointments"), "My Appointments", "Find your appointments using your name and phone number.")

@app.route("/patient/profile", methods=["GET","POST"])
def patient_profile():
    if request.method == "POST":
        patient = find_patient(request.form.get("name",""), request.form.get("phone",""))
        if not patient:
            flash("Patient profile not found.")
            return redirect(url_for("patient_profile"))
        body = """
        <div class="header"><div><h1>My Profile</h1><p>Patient record.</p></div><a class="btn" href="{{ url_for('patient_portal') }}">Back to Patient Portal</a></div>
        <div class="card"><div class="grid" style="grid-template-columns:repeat(2,1fr)">
          <div><p><b>Patient ID</b></p><div class="kpi">{{p.id}}</div></div><div><p><b>Full Name</b></p><div class="kpi" style="font-size:22px">{{p.name}}</div></div>
          <div><p><b>Age</b></p><div class="kpi">{{p.age}}</div></div><div><p><b>Gender</b></p><div class="kpi" style="font-size:22px">{{p.gender}}</div></div>
          <div><p><b>Contact Number</b></p><div class="kpi" style="font-size:22px">{{p.phone}}</div></div><div><p><b>Email</b></p><div class="kpi" style="font-size:18px">{{p.email}}</div></div>
        </div></div>
        """
        return page("My Profile", body, p=patient)
    return identity_form(url_for("patient_profile"), "My Profile", "Find your patient profile.")

@app.route("/patient/prescription", methods=["GET","POST"])
def patient_prescription():
    if request.method == "POST":
        patient = find_patient(request.form.get("name",""), request.form.get("phone",""))
        if not patient:
            flash("Patient profile not found.")
            return redirect(url_for("patient_prescription"))
        data = [p for p in prescriptions if p["patient_id"] == patient["id"]]
        body = """
        <div class="header"><div><h1>My Prescription</h1><p>Prescription history for {{p.name}}.</p></div><a class="btn" href="{{ url_for('patient_portal') }}">Back to Patient Portal</a></div>
        {% if not data %}<div class="empty">No prescription available.</div>
        {% else %}{% for rx in data %}<div class="card" style="margin-bottom:15px"><h3>{{rx.doctor_name}}</h3>
        <p><b>Patient:</b> {{p.name}} &nbsp; <b>Patient ID:</b> {{p.id}}</p>
        <table><tr><th>Medicine</th><th>Dosage</th><th>Frequency</th><th>Duration</th></tr>
        {% for m in rx.medicines %}<tr><td>{{m.name}}</td><td>{{m.dosage}}</td><td>{{m.frequency}}</td><td>{{m.duration}}</td></tr>{% endfor %}
        </table></div>{% endfor %}{% endif %}
        """
        return page("My Prescription", body, p=patient, data=data)
    return identity_form(url_for("patient_prescription"), "My Prescription", "Find prescriptions using your name and phone number.")

@app.route("/patient/bill", methods=["GET","POST"])
def patient_bill():
    if request.method == "POST":
        patient = find_patient(request.form.get("name",""), request.form.get("phone",""))
        if not patient:
            flash("Patient record not found.")
            return redirect(url_for("patient_bill"))
        bill = next((b for b in bills if b["patient_id"] == patient["id"]), None)
        if not bill:
            flash("No cash bill has been generated yet.")
            return redirect(url_for("patient_bill"))
        body = """
        <div class="header"><div><h1>Cash Bill</h1><p>City Care Hospital.</p></div><a class="btn" href="{{ url_for('patient_portal') }}">Back to Patient Portal</a></div>
        <div class="card">
          <p><b>Patient Name:</b> {{p.name}}</p><p><b>Patient ID:</b> {{p.id}}</p><p><b>Age:</b> {{p.age}}</p><p><b>Gender:</b> {{p.gender}}</p><p><b>Contact:</b> {{p.phone}}</p><hr>
          <table><tr><th>Charge</th><th>Amount</th></tr><tr><td>Consultation Fee</td><td>AED {{'%.2f'|format(b.consultation)}}</td></tr><tr><td>Medicine Charges</td><td>AED {{'%.2f'|format(b.medicine)}}</td></tr><tr><td>Other Charges</td><td>AED {{'%.2f'|format(b.other)}}</td></tr></table>
          <p class="bill-total">TOTAL: AED {{'%.2f'|format(b.total)}}</p>
        </div>
        """
        return page("Cash Bill", body, p=patient, b=bill)
    return identity_form(url_for("patient_bill"), "Cash Bill", "Find your cash bill using your name and phone number.")

# ==============================================================
# DOCTOR PORTAL
# ==============================================================

@app.route("/doctor/login", methods=["GET","POST"])
def doctor_login():
    if request.method == "POST":
        doctor = find_doctor(request.form.get("doctor_id","").strip().upper())
        if not doctor:
            flash("Invalid Doctor ID.")
            return redirect(url_for("doctor_login"))
        session["role"]="doctor"; session["doctor_id"]=doctor["id"]
        return redirect(url_for("doctor_portal"))
    body = """
    <div class="header"><div><h1>Doctor Login</h1><p>Enter your Doctor ID.</p></div><a class="btn" href="{{ url_for('home') }}">Back Home</a></div>
    <div class="card form-card"><form method="post"><div class="field"><label>Doctor ID</label><input name="doctor_id" placeholder="Example: D101" required></div><button class="btn primary">LOGIN</button></form></div>
    """
    return page("Doctor Login", body)

def current_doctor():
    return find_doctor(session.get("doctor_id",""))

@app.route("/doctor")
@role_required("doctor")
def doctor_portal():
    doctor = current_doctor()
    body = """
    <div class="hero"><h1>Doctor Portal</h1><p>Welcome, {{doctor.name}} • {{doctor.department}}</p></div>
    <div class="grid">
      <div class="card"><h3>My Patients</h3><p>Patients assigned through your appointments.</p><a class="btn primary" href="{{url_for('doctor_patients')}}">Open</a></div>
      <div class="card"><h3>My Appointments</h3><p>View your scheduled appointments.</p><a class="btn" href="{{url_for('doctor_appointments')}}">Open</a></div>
      <div class="card"><h3>Prescribe Medicine</h3><p>Create a prescription for an assigned patient.</p><a class="btn" href="{{url_for('doctor_prescribe')}}">Open</a></div>
    </div>
    """
    return page("Doctor Portal", body, doctor=doctor)

@app.route("/doctor/patients")
@role_required("doctor")
def doctor_patients():
    doctor = current_doctor()
    data = [a for a in appointments if a["doctor_id"] == doctor["id"]]
    body = """
    <div class="header"><div><h1>My Patients</h1><p>{{doctor.name}}</p></div><a class="btn" href="{{url_for('doctor_portal')}}">Back to Doctor Portal</a></div>
    {% if not data %}<div class="empty">No patients are currently assigned to this doctor.</div>
    {% else %}<div class="card"><table><tr><th>Patient ID</th><th>Patient Name</th><th>Age</th><th>Contact</th></tr>
    {% for a in data %}<tr><td>{{a.patient_id}}</td><td>{{a.patient_name}}</td><td>{{a.age}}</td><td>{{a.phone}}</td></tr>{% endfor %}</table></div>{% endif %}
    """
    return page("My Patients", body, doctor=doctor, data=data)

@app.route("/doctor/appointments")
@role_required("doctor")
def doctor_appointments():
    doctor = current_doctor()
    data = [a for a in appointments if a["doctor_id"] == doctor["id"]]
    body = """
    <div class="header"><div><h1>My Appointments</h1><p>{{doctor.name}}</p></div><a class="btn" href="{{url_for('doctor_portal')}}">Back to Doctor Portal</a></div>
    {% if not data %}<div class="empty">No appointments found.</div>
    {% else %}<div class="card"><table><tr><th>Online No.</th><th>Patient</th><th>Date</th><th>Time</th><th>Token</th></tr>
    {% for a in data %}<tr><td>{{a.online_number}}</td><td>{{a.patient_name}}</td><td>{{a.date}}</td><td>{{a.time}}</td><td>{{a.hospital_token or 'Pending'}}</td></tr>{% endfor %}</table></div>{% endif %}
    """
    return page("Doctor Appointments", body, doctor=doctor, data=data)

@app.route("/doctor/prescribe", methods=["GET","POST"])
@role_required("doctor")
def doctor_prescribe():
    doctor = current_doctor()
    if request.method == "POST":
        patient = find_patient(request.form.get("name",""), request.form.get("phone",""))
        if not patient:
            flash("Patient record not found.")
            return redirect(url_for("doctor_prescribe"))
        assigned = any(a["doctor_id"]==doctor["id"] and a["patient_id"]==patient["id"] for a in appointments)
        if not assigned:
            flash("This patient is not assigned to your doctor.")
            return redirect(url_for("doctor_prescribe"))
        medicine = request.form.get("medicine","").strip()
        dosage = request.form.get("dosage","").strip()
        frequency = request.form.get("frequency","").strip()
        duration = request.form.get("duration","").strip()
        if not all([medicine,dosage,frequency,duration]):
            flash("Please complete all medicine fields.")
            return redirect(url_for("doctor_prescribe"))
        prescriptions.append({
            "patient_id":patient["id"],"patient_name":patient["name"],"doctor_id":doctor["id"],"doctor_name":doctor["name"],
            "medicines":[{"name":medicine,"dosage":dosage,"frequency":frequency,"duration":duration}]
        })
        flash("Prescription saved successfully.")
        return redirect(url_for("doctor_portal"))
    body = """
    <div class="header"><div><h1>Prescribe Medicine</h1><p>Only patients assigned to your doctor can receive a prescription.</p></div><a class="btn" href="{{url_for('doctor_portal')}}">Back to Doctor Portal</a></div>
    <div class="card form-card"><form method="post">
      <div class="two"><div class="field"><label>Patient Name</label><input name="name" required></div><div class="field"><label>Phone Number</label><input name="phone" required></div></div>
      <div class="field"><label>Medicine</label><input name="medicine" required></div>
      <div class="two"><div class="field"><label>Dosage</label><input name="dosage" placeholder="e.g. 500 mg" required></div><div class="field"><label>Frequency</label><input name="frequency" placeholder="e.g. Twice daily" required></div></div>
      <div class="field"><label>Duration</label><input name="duration" placeholder="e.g. 5 days" required></div>
      <button class="btn primary">SAVE PRESCRIPTION</button>
    </form></div>
    """
    return page("Prescribe Medicine", body)

# ==============================================================
# RECEPTIONIST PORTAL
# ==============================================================

@app.route("/receptionist/login", methods=["GET","POST"])
def receptionist_login():
    if request.method == "POST":
        rid = request.form.get("receptionist_id","").strip().upper()
        rec = next((r for r in receptionists if r["id"] == rid), None)
        if not rec:
            flash("Invalid Receptionist ID.")
            return redirect(url_for("receptionist_login"))
        session["role"]="receptionist"; session["receptionist_id"]=rid
        return redirect(url_for("receptionist_portal"))
    body = """
    <div class="header"><div><h1>Receptionist Login</h1><p>Enter your Receptionist ID.</p></div><a class="btn" href="{{url_for('home')}}">Back Home</a></div>
    <div class="card form-card"><form method="post"><div class="field"><label>Receptionist ID</label><input name="receptionist_id" placeholder="Example: R001" required></div><button class="btn primary">LOGIN</button></form></div>
    """
    return page("Receptionist Login", body)

@app.route("/receptionist")
@role_required("receptionist")
def receptionist_portal():
    body = """
    <div class="hero"><h1>Receptionist Portal</h1><p>Manage front-desk hospital operations.</p></div>
    <div class="grid">
      <div class="card"><h3>Online Booking Search</h3><p>Find an online booking and check the patient in.</p><a class="btn primary" href="{{url_for('find_booking')}}">Open</a></div>
      <div class="card"><h3>Walk-in Patient</h3><p>Register a patient arriving without an online appointment.</p><a class="btn" href="{{url_for('walk_in')}}">Open</a></div>
      <div class="card"><h3>Patient Records</h3><p>View all registered patient records.</p><a class="btn" href="{{url_for('patient_records')}}">Open</a></div>
      <div class="card"><h3>Appointment Schedule</h3><p>View all hospital appointments.</p><a class="btn" href="{{url_for('all_appointments')}}">Open</a></div>
      <div class="card"><h3>Generate Cash Bill</h3><p>Create or update a patient's cash bill.</p><a class="btn" href="{{url_for('generate_bill')}}">Open</a></div>
    </div>
    """
    return page("Receptionist Portal", body)

@app.route("/receptionist/booking", methods=["GET","POST"])
@role_required("receptionist")
def find_booking():
    if request.method == "POST":
        name = request.form.get("name","").strip()
        number = request.form.get("online_number","").strip().upper()
        a = next((x for x in appointments if x["patient_name"].lower()==name.lower() and x["online_number"].upper()==number), None)
        if not a:
            flash("Appointment not found. Check the patient name and online booking number.")
            return redirect(url_for("find_booking"))
        if not a["hospital_token"]:
            global hospital_token_counter
            a["hospital_token"] = "T" + str(hospital_token_counter).zfill(3)
            hospital_token_counter += 1
        body = """
        <div class="header"><div><h1>Patient Checked In</h1><p>Online booking found successfully.</p></div><a class="btn" href="{{url_for('receptionist_portal')}}">Back to Receptionist Portal</a></div>
        <div class="card"><h3>{{a.patient_name}}</h3><p><b>Online Booking:</b> {{a.online_number}}</p><p><b>Hospital Token:</b> <span class="pill">{{a.hospital_token}}</span></p><p><b>Doctor:</b> {{a.doctor_name}}</p><p><b>Date:</b> {{a.date}} &nbsp; <b>Time:</b> {{a.time}}</p></div>
        """
        return page("Check In", body, a=a)
    body = """
    <div class="header"><div><h1>Online Booking Search</h1><p>Find a booking using patient name and online booking number.</p></div><a class="btn" href="{{url_for('receptionist_portal')}}">Back to Receptionist Portal</a></div>
    <div class="card form-card"><form method="post"><div class="field"><label>Patient Name</label><input name="name" required></div><div class="field"><label>Online Booking Number</label><input name="online_number" placeholder="Example: O001" required></div><button class="btn primary">SEARCH & CHECK IN</button></form></div>
    """
    return page("Online Booking Search", body)

@app.route("/receptionist/walkin", methods=["GET","POST"])
@role_required("receptionist")
def walk_in():
    global patient_counter, hospital_token_counter
    if request.method == "POST":
        data = {k: request.form.get(k,"").strip() for k in ["name","age","gender","phone","email"]}
        if not all(data.values()):
            flash("Please fill in all patient details.")
            return redirect(url_for("walk_in"))
        if not data["age"].isdigit():
            flash("Age must be a number.")
            return redirect(url_for("walk_in"))
        patient_id = "P" + str(patient_counter); patient_counter += 1
        patient = {"id":patient_id,"name":data["name"],"age":data["age"],"gender":data["gender"],"phone":data["phone"],"email":data["email"]}
        patients.append(patient)
        token = "T" + str(hospital_token_counter).zfill(3); hospital_token_counter += 1
        body = """
        <div class="header"><div><h1>Walk-in Registered</h1><p>Patient registered successfully.</p></div><a class="btn" href="{{url_for('receptionist_portal')}}">Back to Receptionist Portal</a></div>
        <div class="card"><p><b>Patient Name:</b> {{p.name}}</p><p><b>Patient ID:</b> {{p.id}}</p><p><b>Hospital Token No.:</b> <span class="pill">{{token}}</span></p></div>
        """
        return page("Walk-in Registered", body, p=patient, token=token)
    body = """
    <div class="header"><div><h1>Walk-in Patient</h1><p>Register a patient arriving without an online appointment.</p></div><a class="btn" href="{{url_for('receptionist_portal')}}">Back to Receptionist Portal</a></div>
    <div class="card form-card"><form method="post">
      <div class="field"><label>Full Name</label><input name="name" required></div>
      <div class="two"><div class="field"><label>Age</label><input name="age" type="number" required></div><div class="field"><label>Gender</label><select name="gender" required><option value="">Select</option><option>Male</option><option>Female</option><option>Other</option></select></div></div>
      <div class="two"><div class="field"><label>Contact Number</label><input name="phone" required></div><div class="field"><label>Email Address</label><input name="email" type="email" required></div></div>
      <button class="btn primary">REGISTER WALK-IN</button>
    </form></div>
    """
    return page("Walk-in Patient", body)

@app.route("/receptionist/records")
@role_required("receptionist")
def patient_records():
    body = """
    <div class="header"><div><h1>Patient Records</h1><p>All registered patients.</p></div><a class="btn" href="{{url_for('receptionist_portal')}}">Back to Receptionist Portal</a></div>
    {% if not patients %}<div class="empty">No patient records available.</div>
    {% else %}<div class="card"><table><tr><th>ID</th><th>Name</th><th>Age</th><th>Gender</th><th>Contact</th><th>Email</th></tr>
    {% for p in patients %}<tr><td>{{p.id}}</td><td>{{p.name}}</td><td>{{p.age}}</td><td>{{p.gender}}</td><td>{{p.phone}}</td><td>{{p.email}}</td></tr>{% endfor %}
    </table></div>{% endif %}
    """
    return page("Patient Records", body, patients=patients)

@app.route("/receptionist/appointments")
@role_required("receptionist")
def all_appointments():
    body = """
    <div class="header"><div><h1>Appointment Schedule</h1><p>All hospital appointments.</p></div><a class="btn" href="{{url_for('receptionist_portal')}}">Back to Receptionist Portal</a></div>
    {% if not appointments %}<div class="empty">No appointments available.</div>
    {% else %}<div class="card"><table><tr><th>Online No.</th><th>Token</th><th>Patient</th><th>Doctor</th><th>Date</th><th>Time</th></tr>
    {% for a in appointments %}<tr><td>{{a.online_number}}</td><td>{{a.hospital_token or 'Pending'}}</td><td>{{a.patient_name}}</td><td>{{a.doctor_name}}</td><td>{{a.date}}</td><td>{{a.time}}</td></tr>{% endfor %}
    </table></div>{% endif %}
    """
    return page("Appointment Schedule", body, appointments=appointments)

@app.route("/receptionist/bill", methods=["GET","POST"])
@role_required("receptionist")
def generate_bill():
    if request.method == "POST":
        patient = find_patient(request.form.get("name",""), request.form.get("phone",""))
        if not patient:
            flash("Patient record not found.")
            return redirect(url_for("generate_bill"))
        try:
            consultation = float(request.form.get("consultation","0"))
            medicine = float(request.form.get("medicine","0"))
            other = float(request.form.get("other","0"))
            if min(consultation,medicine,other) < 0: raise ValueError
        except ValueError:
            flash("All charges must be valid non-negative numbers.")
            return redirect(url_for("generate_bill"))
        total = consultation + medicine + other
        bill = next((b for b in bills if b["patient_id"] == patient["id"]), None)
        if bill:
            bill.update(consultation=consultation,medicine=medicine,other=other,total=total)
        else:
            bill = {"patient_id":patient["id"],"patient_name":patient["name"],"consultation":consultation,"medicine":medicine,"other":other,"total":total}
            bills.append(bill)
        body = """
        <div class="header"><div><h1>Cash Bill Saved</h1><p>Bill generated successfully.</p></div><a class="btn" href="{{url_for('receptionist_portal')}}">Back to Receptionist Portal</a></div>
        <div class="card"><p><b>Patient:</b> {{p.name}}</p><p><b>Patient ID:</b> {{p.id}}</p><table><tr><th>Charge</th><th>Amount</th></tr><tr><td>Consultation Fee</td><td>AED {{'%.2f'|format(b.consultation)}}</td></tr><tr><td>Medicine Charges</td><td>AED {{'%.2f'|format(b.medicine)}}</td></tr><tr><td>Other Charges</td><td>AED {{'%.2f'|format(b.other)}}</td></tr></table><p class="bill-total">TOTAL: AED {{'%.2f'|format(b.total)}}</p></div>
        """
        return page("Cash Bill Saved", body, p=patient, b=bill)
    body = """
    <div class="header"><div><h1>Generate Cash Bill</h1><p>Enter patient billing details.</p></div><a class="btn" href="{{url_for('receptionist_portal')}}">Back to Receptionist Portal</a></div>
    <div class="card form-card"><form method="post">
      <div class="two"><div class="field"><label>Patient Name</label><input name="name" required></div><div class="field"><label>Phone Number</label><input name="phone" required></div></div>
      <div class="two"><div class="field"><label>Consultation Fee</label><input name="consultation" type="number" step="0.01" min="0" required></div><div class="field"><label>Medicine Charges</label><input name="medicine" type="number" step="0.01" min="0" required></div></div>
      <div class="field"><label>Other Charges</label><input name="other" type="number" step="0.01" min="0" required></div>
      <button class="btn primary">SAVE BILL</button>
    </form></div>
    """
    return page("Generate Cash Bill", body)

if __name__ == "__main__":
    print("=" * 60)
    print("CITY CARE HOSPITAL - WEB VERSION")
    print("Open http://127.0.0.1:5000 in your browser.")
    print("=" * 60)
    app.run(debug=True)
