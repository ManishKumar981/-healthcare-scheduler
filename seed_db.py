from models import get_db, init_db

init_db()
db = get_db()

# Clear existing data
db.execute("DELETE FROM appointments")
db.execute("DELETE FROM time_slots")
db.execute("DELETE FROM patients")
db.execute("DELETE FROM doctors")
db.commit()

doctors = [
    ("Dr. Priya Sharma",  "General Medicine"),
    ("Dr. Arjun Mehta",   "Cardiology"),
    ("Dr. Sneha Reddy",   "Dermatology"),
]
for name, spec in doctors:
    db.execute("INSERT INTO doctors (name, specialty) VALUES (?,?)", (name, spec))

patients = [
    ("Ravi Kumar",   45, "Male",   "9000000001", "ravi@mail.com",    "pass123", 2, 8.5),
    ("Anita Singh",  32, "Female", "9000000002", "anita@mail.com",   "pass123", 0, 3.2),
    ("Mohan Das",    60, "Male",   "9000000003", "mohan@mail.com",   "pass123", 5, 18.0),
    ("Lakshmi Nair", 27, "Female", "9000000004", "lakshmi@mail.com", "pass123", 1, 5.0),
]
for p in patients:
    db.execute("INSERT INTO patients (name,age,gender,contact,email,password,previous_noshows,distance_km) VALUES (?,?,?,?,?,?,?,?)", p)

db.commit()
db.close()
print("Database seeded with 3 doctors and 4 patients.")
print("Demo login: ravi@mail.com / pass123")
