from flask import Blueprint, request, jsonify, render_template
from models import get_db
from ai_modules.simulation import run_simulation
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/')
def dashboard():
    return render_template('admin/dashboard.html')


@admin_bp.route('/stats', methods=['GET'])
def stats():
    db = get_db()
    try:
        def count(sql, args=()):
            return db.execute(sql, args).fetchone()[0]
        return jsonify({
            'total_patients'    : count("SELECT COUNT(*) FROM patients"),
            'total_appointments': count("SELECT COUNT(*) FROM appointments"),
            'total_doctors'     : count("SELECT COUNT(*) FROM doctors"),
            'no_shows'          : count("SELECT COUNT(*) FROM appointments WHERE status='no-show'"),
            'scheduled'         : count("SELECT COUNT(*) FROM appointments WHERE status='scheduled'"),
            'completed'         : count("SELECT COUNT(*) FROM appointments WHERE status='completed'"),
            'cancelled'         : count("SELECT COUNT(*) FROM appointments WHERE status='cancelled'"),
        })
    finally:
        db.close()


@admin_bp.route('/add_doctor', methods=['POST'])
def add_doctor():
    data = request.get_json()
    db   = get_db()
    try:
        cur = db.execute("INSERT INTO doctors (name, specialty) VALUES (?,?)", (data['name'], data['specialty']))
        db.commit()
        return jsonify({'message': 'Doctor added successfully', 'doctor_id': cur.lastrowid}), 201
    finally:
        db.close()


@admin_bp.route('/doctors', methods=['GET'])
def list_doctors():
    db = get_db()
    try:
        rows = db.execute("SELECT * FROM doctors").fetchall()
        return jsonify([dict(r) for r in rows])
    finally:
        db.close()


@admin_bp.route('/generate_slots', methods=['POST'])
def generate_slots():
    data       = request.get_json()
    doctor_id  = data['doctor_id']
    slot_date  = data['date']
    start_hour = int(data.get('start_hour', 9))
    end_hour   = int(data.get('end_hour', 17))

    db = get_db()
    try:
        db.execute("DELETE FROM time_slots WHERE doctor_id=? AND slot_date=?", (doctor_id, slot_date))
        current = datetime.strptime(f"{start_hour}:00", '%H:%M')
        end     = datetime.strptime(f"{end_hour}:00",   '%H:%M')
        created = 0
        while current < end:
            slot_end = current + timedelta(minutes=15)
            db.execute(
                "INSERT INTO time_slots (doctor_id,slot_date,start_time,end_time,is_available,can_overbook) VALUES (?,?,?,?,1,0)",
                (doctor_id, slot_date, current.strftime('%H:%M'), slot_end.strftime('%H:%M'))
            )
            current  = slot_end
            created += 1
        db.commit()
        return jsonify({'message': f'{created} slots created for doctor {doctor_id} on {slot_date}'}), 201
    finally:
        db.close()


@admin_bp.route('/schedule/<string:date_str>', methods=['GET'])
def view_schedule(date_str):
    db = get_db()
    try:
        rows = db.execute(
            '''SELECT a.appointment_id, p.name as patient_name, d.name as doctor_name,
                      s.start_time, s.end_time, a.status, a.no_show_prob, a.priority_score, a.urgency_level
               FROM appointments a
               JOIN patients   p ON a.patient_id = p.patient_id
               JOIN doctors    d ON a.doctor_id   = d.doctor_id
               JOIN time_slots s ON a.slot_id     = s.slot_id
               WHERE a.appointment_date=?
               ORDER BY s.start_time''',
            (date_str,)
        ).fetchall()
        result = []
        for r in rows:
            r = dict(r)
            r['time_slot']   = f"{r['start_time']} - {r['end_time']}"
            r['risk_level']  = 'HIGH' if r['no_show_prob'] >= 0.7 else 'MEDIUM' if r['no_show_prob'] >= 0.4 else 'LOW'
            result.append(r)
        return jsonify(result)
    finally:
        db.close()


@admin_bp.route('/mark_noshow/<int:appointment_id>', methods=['PUT'])
def mark_noshow(appointment_id):
    db = get_db()
    try:
        appt = db.execute("SELECT * FROM appointments WHERE appointment_id=?", (appointment_id,)).fetchone()
        if not appt: return jsonify({'error': 'Not found'}), 404
        db.execute("UPDATE appointments SET status='no-show' WHERE appointment_id=?", (appointment_id,))
        db.execute("UPDATE patients SET previous_noshows=previous_noshows+1 WHERE patient_id=?", (appt['patient_id'],))
        db.commit()
        return jsonify({'message': 'Marked as no-show'})
    finally:
        db.close()


@admin_bp.route('/mark_completed/<int:appointment_id>', methods=['PUT'])
def mark_completed(appointment_id):
    db = get_db()
    try:
        db.execute("UPDATE appointments SET status='completed' WHERE appointment_id=?", (appointment_id,))
        db.commit()
        return jsonify({'message': 'Marked as completed'})
    finally:
        db.close()


@admin_bp.route('/simulate', methods=['POST'])
def simulate():
    data     = request.get_json()
    baseline = run_simulation(num_doctors=data.get('num_doctors', 3), no_show_rate=0.25, appt_interval=10)
    optimized= run_simulation(num_doctors=data.get('num_doctors', 3), no_show_rate=data.get('no_show_rate', 0.10), appt_interval=8)
    return jsonify({
        'baseline_results' : baseline,
        'optimized_results': optimized,
        'improvement': {
            'wait_time_reduced_by'  : round(baseline['avg_wait_minutes']  - optimized['avg_wait_minutes'], 2),
            'utilization_gained_pct': round(optimized['utilization_pct']  - baseline['utilization_pct'],   2),
            'more_patients_seen'    : optimized['total_seen'] - baseline['total_seen']
        }
    })


@admin_bp.route('/patients', methods=['GET'])
def list_patients():
    db = get_db()
    try:
        rows = db.execute("SELECT * FROM patients ORDER BY patient_id").fetchall()
        return jsonify([dict(r) for r in rows])
    finally:
        db.close()
