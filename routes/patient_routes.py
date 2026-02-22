from flask import Blueprint, request, jsonify, render_template
from models import get_db
from ai_modules.scheduler import allocate_appointment_db
from datetime import date, datetime

patient_bp = Blueprint('patient', __name__)


# ── HOME ────────────────────────────────────────────────────────
@patient_bp.route('/')
def index():
    return render_template('patient/dashboard.html')


# ── REGISTER PAGE (GET) ─────────────────────────────────────────
@patient_bp.route('/register', methods=['GET'])
def register_page():
    return render_template('patient/dashboard.html')


# ── REGISTER SUBMIT (POST) ──────────────────────────────────────
@patient_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    db   = get_db()
    try:
        existing = db.execute(
            "SELECT patient_id FROM patients WHERE email=?",
            (data['email'],)
        ).fetchone()

        if existing:
            return jsonify({'error': 'Email already registered'}), 400

        cur = db.execute(
            """INSERT INTO patients
               (name, age, gender, contact, email, password,
                previous_noshows, distance_km)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data['name'],
                int(data['age']),
                data['gender'],
                data['contact'],
                data['email'],
                data['password'],
                int(data.get('previous_noshows', 0)),
                float(data.get('distance_km', 5.0))
            )
        )
        db.commit()
        return jsonify({
            'message'   : 'Patient registered successfully',
            'patient_id': cur.lastrowid
        }), 201

    finally:
        db.close()


# ── LOGIN ────────────────────────────────────────────────────────
@patient_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    db   = get_db()
    try:
        patient = db.execute(
            "SELECT * FROM patients WHERE email=? AND password=?",
            (data['email'], data['password'])
        ).fetchone()

        if not patient:
            return jsonify({'error': 'Invalid email or password'}), 401

        return jsonify({
            'message'   : 'Login successful',
            'patient_id': patient['patient_id'],
            'name'      : patient['name']
        }), 200

    finally:
        db.close()


# ── BOOK APPOINTMENT ─────────────────────────────────────────────
@patient_bp.route('/book', methods=['POST'])
def book_appointment():
    data = request.get_json()
    db   = get_db()
    try:
        patient = db.execute(
            "SELECT * FROM patients WHERE patient_id=?",
            (data['patient_id'],)
        ).fetchone()

        doctor = db.execute(
            "SELECT * FROM doctors WHERE doctor_id=?",
            (data['doctor_id'],)
        ).fetchone()

        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        if not doctor:
            return jsonify({'error': 'Doctor not found'}), 404

        appt_date = data['appointment_date']
        today_str = date.today().isoformat()

        if appt_date < today_str:
            return jsonify({
                'error': 'Cannot book appointments in the past'
            }), 400

        # Get available slots for this doctor on selected date
        slots = db.execute(
            """SELECT * FROM time_slots
               WHERE doctor_id=? AND slot_date=? AND is_available=1
               ORDER BY start_time""",
            (data['doctor_id'], appt_date)
        ).fetchall()

        if not slots:
            return jsonify({
                'error': 'No available slots for this doctor on that date.'
                         ' Ask admin to generate slots first.'
            }), 404

        urgency = int(data.get('urgency_level', 1))

        # AI Scheduling — predict no-show + allocate optimal slot
        slot, no_show_prob, priority, is_overbooked = allocate_appointment_db(
            dict(patient), list(slots), appt_date, today_str, urgency
        )

        if slot is None:
            return jsonify({'error': 'Could not allocate a slot'}), 404

        # Update slot availability based on risk
        if not is_overbooked:
            # Normal patient — close the slot
            db.execute(
                "UPDATE time_slots SET is_available=0 WHERE slot_id=?",
                (slot['slot_id'],)
            )
        else:
            # High-risk patient — keep slot open for overbooking
            db.execute(
                "UPDATE time_slots SET can_overbook=1 WHERE slot_id=?",
                (slot['slot_id'],)
            )

        # Save appointment to database
        cur = db.execute(
            """INSERT INTO appointments
               (patient_id, doctor_id, slot_id, appointment_date,
                no_show_prob, priority_score, urgency_level)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                patient['patient_id'],
                doctor['doctor_id'],
                slot['slot_id'],
                appt_date,
                no_show_prob,
                priority,
                urgency
            )
        )
        db.commit()

        # Determine risk label
        if no_show_prob >= 0.70:
            risk = 'HIGH'
        elif no_show_prob >= 0.40:
            risk = 'MEDIUM'
        else:
            risk = 'LOW'

        return jsonify({
            'message'            : 'Appointment booked successfully',
            'appointment_id'     : cur.lastrowid,
            'doctor'             : doctor['name'],
            'slot'               : f"{slot['start_time']} - {slot['end_time']}",
            'date'               : appt_date,
            'no_show_probability': no_show_prob,
            'no_show_risk'       : risk,
            'is_overbooked'      : is_overbooked,
            'priority_score'     : priority
        }), 201

    finally:
        db.close()


# ── VIEW MY APPOINTMENTS ─────────────────────────────────────────
@patient_bp.route('/appointments/<int:patient_id>', methods=['GET'])
def get_appointments(patient_id):
    db = get_db()
    try:
        rows = db.execute(
            """SELECT a.*, s.start_time, s.end_time,
                      d.name as doctor_name
               FROM appointments a
               JOIN time_slots s ON a.slot_id    = s.slot_id
               JOIN doctors    d ON a.doctor_id  = d.doctor_id
               WHERE a.patient_id = ?
               ORDER BY a.appointment_date DESC""",
            (patient_id,)
        ).fetchall()

        result = []
        for r in rows:
            r = dict(r)
            r['slot_time'] = f"{r['start_time']} - {r['end_time']}"
            if r['no_show_prob'] >= 0.7:
                r['risk'] = 'HIGH'
            elif r['no_show_prob'] >= 0.4:
                r['risk'] = 'MEDIUM'
            else:
                r['risk'] = 'LOW'
            result.append(r)

        return jsonify(result)

    finally:
        db.close()


# ── CANCEL APPOINTMENT ───────────────────────────────────────────
@patient_bp.route('/cancel/<int:appointment_id>', methods=['PUT'])
def cancel_appointment(appointment_id):
    db = get_db()
    try:
        appt = db.execute(
            "SELECT * FROM appointments WHERE appointment_id=?",
            (appointment_id,)
        ).fetchone()

        if not appt:
            return jsonify({'error': 'Appointment not found'}), 404

        db.execute(
            "UPDATE appointments SET status='cancelled' WHERE appointment_id=?",
            (appointment_id,)
        )
        # Re-open the slot for other patients
        db.execute(
            "UPDATE time_slots SET is_available=1, can_overbook=0 WHERE slot_id=?",
            (appt['slot_id'],)
        )
        db.commit()
        return jsonify({'message': 'Appointment cancelled successfully'})

    finally:
        db.close()


# ── LIST ALL DOCTORS ─────────────────────────────────────────────
@patient_bp.route('/doctors', methods=['GET'])
def list_doctors():
    db = get_db()
    try:
        rows = db.execute(
            "SELECT * FROM doctors WHERE available=1"
        ).fetchall()
        return jsonify([dict(r) for r in rows])
    finally:
        db.close()