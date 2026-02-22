from models import db

class Doctor(db.Model):
    __tablename__ = 'doctors'

    doctor_id  = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    specialty  = db.Column(db.String(100), nullable=False)
    available  = db.Column(db.Boolean, default=True)

    slots        = db.relationship('TimeSlot',    backref='doctor', lazy=True)
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)

    def to_dict(self):
        return {
            'doctor_id' : self.doctor_id,
            'name'      : self.name,
            'specialty' : self.specialty,
            'available' : self.available
        }
