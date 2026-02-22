from models import db
from datetime import datetime

class TimeSlot(db.Model):
    __tablename__ = 'time_slots'

    slot_id      = db.Column(db.Integer, primary_key=True)
    doctor_id    = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'), nullable=False)
    slot_date    = db.Column(db.Date,    nullable=False)
    start_time   = db.Column(db.String(10), nullable=False)
    end_time     = db.Column(db.String(10), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    can_overbook = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'slot_id'     : self.slot_id,
            'doctor_id'   : self.doctor_id,
            'slot_date'   : str(self.slot_date),
            'start_time'  : self.start_time,
            'end_time'    : self.end_time,
            'is_available': self.is_available
        }


class Appointment(db.Model):
    __tablename__ = 'appointments'

    appointment_id   = db.Column(db.Integer, primary_key=True)
    patient_id       = db.Column(db.Integer, db.ForeignKey('patients.patient_id'),  nullable=False)
    doctor_id        = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'),    nullable=False)
    slot_id          = db.Column(db.Integer, db.ForeignKey('time_slots.slot_id'),   nullable=False)
    appointment_date = db.Column(db.Date,    nullable=False)
    status           = db.Column(db.String(20), default='scheduled')
    no_show_prob     = db.Column(db.Float, default=0.0)
    urgency_level    = db.Column(db.Integer, default=1)
    priority_score   = db.Column(db.Float, default=0.0)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)

    slot = db.relationship('TimeSlot', backref='appointments', lazy=True)

    def to_dict(self):
        return {
            'appointment_id'  : self.appointment_id,
            'patient_id'      : self.patient_id,
            'doctor_id'       : self.doctor_id,
            'slot_id'         : self.slot_id,
            'date'            : str(self.appointment_date),
            'status'          : self.status,
            'no_show_prob'    : self.no_show_prob,
            'priority_score'  : self.priority_score,
            'urgency_level'   : self.urgency_level
        }
