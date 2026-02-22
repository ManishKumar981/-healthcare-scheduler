from models import db
from datetime import datetime

class Patient(db.Model):
    __tablename__ = 'patients'

    patient_id       = db.Column(db.Integer, primary_key=True)
    name             = db.Column(db.String(100), nullable=False)
    age              = db.Column(db.Integer,     nullable=False)
    gender           = db.Column(db.String(10),  nullable=False)
    contact          = db.Column(db.String(15),  nullable=False)
    email            = db.Column(db.String(100), unique=True, nullable=False)
    password         = db.Column(db.String(200), nullable=False)
    previous_noshows = db.Column(db.Integer, default=0)
    distance_km      = db.Column(db.Float,   default=5.0)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)

    appointments = db.relationship('Appointment', backref='patient', lazy=True)

    def to_dict(self):
        return {
            'patient_id'      : self.patient_id,
            'name'            : self.name,
            'age'             : self.age,
            'gender'          : self.gender,
            'contact'         : self.contact,
            'email'           : self.email,
            'previous_noshows': self.previous_noshows,
            'distance_km'     : self.distance_km
        }
