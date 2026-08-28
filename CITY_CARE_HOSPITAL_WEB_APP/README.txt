CITY CARE HOSPITAL - WEB VERSION

QUICK START
1. Install Python.
2. Open a terminal in this folder.
3. Run:
   pip install -r requirements.txt
4. Run:
   python app.py
5. Open:
   http://127.0.0.1:5000

LOGIN IDS
Doctor IDs: D101 to D109
Receptionist IDs: R001 to R003

IMPORTANT
This is a school-project demo. Data is stored in memory, so it resets when
the Python program is stopped. For a deployed version, a database such as
SQLite should be added.

DEPLOYMENT
This app is structured as a normal Flask web app and can be deployed to
services such as Render. Use:
Build command: pip install -r requirements.txt
Start command: gunicorn app:app
