# AI-Based Healthcare Appointment Scheduling Optimization System
### Final Year Project | Python + Flask + scikit-learn + SimPy

---

## Quick Start (Windows)

### Option A — One-Click Setup (Recommended)
Double-click `RUN_PROJECT.bat`
This will automatically:
1. Create virtual environment
2. Install all dependencies
3. Generate training data
4. Train the ML model
5. Seed the database with sample data
6. Start the Flask server

### Option B — Manual Setup
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python data\generate_data.py
python ai_modules\no_show_predictor.py
python seed_db.py
python app.py
```

---

## Access the Application

After running, open your browser:

| Portal | URL |
|--------|-----|
| Home Page | http://127.0.0.1:5000 |
| Patient Portal | http://127.0.0.1:5000/patient/ |
| Admin Dashboard | http://127.0.0.1:5000/admin/ |

---

## Demo Credentials

### Patient Login
- Email: ravi@mail.com | Password: pass123
- Email: anita@mail.com | Password: pass123
- Email: mohan@mail.com | Password: pass123

---

## Project Structure

```
healthcare_scheduler/
├── app.py                    Main Flask application
├── config.py                 Configuration settings
├── seed_db.py                Database seeder with sample data
├── RUN_PROJECT.bat           One-click Windows launcher
├── requirements.txt          Python dependencies
│
├── ai_modules/
│   ├── no_show_predictor.py  Random Forest ML model
│   ├── scheduler.py          Priority-weighted slot allocator
│   └── simulation.py         SimPy discrete-event simulation
│
├── models/
│   ├── patient.py            Patient database model
│   ├── doctor.py             Doctor database model
│   └── appointment.py        Appointment + TimeSlot models
│
├── routes/
│   ├── patient_routes.py     Patient API endpoints
│   └── admin_routes.py       Admin API endpoints
│
├── templates/
│   ├── index.html            Landing page
│   ├── patient/dashboard.html Patient portal (register/book/view)
│   └── admin/dashboard.html  Admin portal (schedule/simulate/manage)
│
└── data/
    ├── generate_data.py      Generates 1200-row synthetic dataset
    └── historical_data.csv   Generated training data (after running)
```

---

## API Endpoints

### Patient APIs
| Method | URL | Description |
|--------|-----|-------------|
| POST | /patient/register | Register new patient |
| POST | /patient/login | Patient login |
| POST | /patient/book | Book appointment (AI scheduling) |
| GET  | /patient/appointments/<id> | View my appointments |
| PUT  | /patient/cancel/<id> | Cancel appointment |
| GET  | /patient/doctors | List available doctors |

### Admin APIs
| Method | URL | Description |
|--------|-----|-------------|
| GET  | /admin/stats | Dashboard statistics |
| POST | /admin/add_doctor | Add new doctor |
| POST | /admin/generate_slots | Generate time slots |
| GET  | /admin/schedule/<date> | View daily schedule |
| PUT  | /admin/mark_noshow/<id> | Mark appointment as no-show |
| PUT  | /admin/mark_completed/<id> | Mark as completed |
| POST | /admin/simulate | Run SimPy simulation |
| GET  | /admin/patients | List all patients |

---

## How to Use (Step by Step)

### As Admin (First Time Setup):
1. Go to http://127.0.0.1:5000/admin/
2. Click "Manage Doctors" → Add doctors (or use pre-seeded ones)
3. Click "Generate Slots" → Select a doctor, pick today's date → Generate
4. Go back to schedule view to see available slots

### As Patient:
1. Go to http://127.0.0.1:5000/patient/
2. Click Register → Fill form → Submit
3. Login with your credentials
4. Click "Book Appointment" → Select doctor, date, urgency → Book
5. AI will show your no-show risk and assigned slot
6. View your appointments in "My Appointments"

### Run Simulation:
1. Go to Admin Dashboard → "Run Simulation"
2. Set number of doctors and optimized no-show rate
3. Click "Run Simulation"
4. Compare baseline vs AI-optimized results in table + chart

---

## AI Components

### 1. No-Show Prediction (Random Forest)
- Features: previous_no_shows, days_until_appointment, appointment_hour,
  day_of_week, age, gender, reminder_sent, distance_km
- Model: RandomForestClassifier (100 trees, max_depth=8, balanced classes)
- Output: Probability 0.0–1.0 → LOW / MEDIUM / HIGH risk

### 2. Priority Score Formula
```
Score = 0.5 × (urgency/5) + 0.3 × (wait_days/30) + 0.2 × (1 - no_show_prob)
```

### 3. Overbooking Strategy
- HIGH risk (≥70%): Slot stays open for another patient
- MEDIUM risk (40–70%): Booked normally, reminder flag set
- LOW risk (<40%): Normal booking, slot closed

### 4. SimPy Simulation
- Discrete-event simulation of 8-hour clinic day
- Baseline: 25% no-show, 10-min intervals
- Optimized: 10% effective no-show (after overbooking), 8-min intervals
- KPIs: wait time, utilization %, patients seen, no-show %

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python 3.11, Flask 3.0 |
| Database | SQLite + SQLAlchemy ORM |
| ML/AI | scikit-learn (Random Forest) |
| Simulation | SimPy (Discrete-Event) |
| Frontend | Bootstrap 5, Chart.js, Font Awesome |
| Data | pandas, numpy |

---

*Final Year Project — AI-Based Healthcare Appointment Scheduling Optimization System*
