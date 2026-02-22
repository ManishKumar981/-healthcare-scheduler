from ai_modules.no_show_predictor import predict_no_show
from datetime import datetime


def build_patient_features(patient, appointment_date, booking_date):
    appt_dt    = datetime.strptime(str(appointment_date), '%Y-%m-%d')
    book_dt    = datetime.strptime(str(booking_date),    '%Y-%m-%d')
    days_until = max((appt_dt - book_dt).days, 0)
    return {
        'previous_no_shows'      : patient.get('previous_noshows', 0) if isinstance(patient, dict) else getattr(patient, 'previous_noshows', 0),
        'days_until_appointment' : days_until,
        'appointment_hour'       : 9,
        'day_of_week'            : appt_dt.weekday(),
        'age'                    : patient.get('age', 30) if isinstance(patient, dict) else getattr(patient, 'age', 30),
        'gender_encoded'         : 1 if (patient.get('gender', '') if isinstance(patient, dict) else getattr(patient, 'gender', '')) == 'Male' else 0,
        'reminder_sent'          : 0,
        'distance_km'            : patient.get('distance_km', 5.0) if isinstance(patient, dict) else getattr(patient, 'distance_km', 5.0)
    }


def compute_priority_score(urgency_level, days_waiting, no_show_prob):
    w1, w2, w3  = 0.5, 0.3, 0.2
    urgency_norm = urgency_level / 5.0
    wait_norm    = min(days_waiting / 30.0, 1.0)
    score        = (w1 * urgency_norm) + (w2 * wait_norm) + (w3 * (1 - no_show_prob))
    return round(score, 4)


def allocate_appointment_db(patient, available_slots, appointment_date, booking_date, urgency_level=1, days_waiting=0):
    """Works with raw SQLite row dicts."""
    features     = build_patient_features(patient, appointment_date, booking_date)
    no_show_prob = predict_no_show(features)
    priority     = compute_priority_score(urgency_level, days_waiting, no_show_prob)

    open_slots = [s for s in available_slots if s['is_available']]
    if not open_slots:
        return None, no_show_prob, priority, False

    selected = open_slots[0]
    is_overbooked = no_show_prob >= 0.70

    return selected, no_show_prob, priority, is_overbooked
