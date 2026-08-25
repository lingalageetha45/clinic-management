
# Seed initial admin user and sample data.
# Safe to run multiple times (skips if admin already exists).

from app.core.database import SessionLocal, engine, Base
from app.models import *
from app.auth.security import get_password_hash
from app.models.user import UserRole


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == "admin@clinic.com").first()
        if admin:
            print("Seed: admin already exists, skipping.")
            return

        admin = User(
            email="admin@clinic.com",
            hashed_password=get_password_hash("admin123"),
            full_name="System Admin",
            role=UserRole.ADMIN,
        )
        db.add(admin)

        receptionist = User(
            email="reception@clinic.com",
            hashed_password=get_password_hash("reception123"),
            full_name="Front Desk",
            role=UserRole.RECEPTIONIST,
        )
        db.add(receptionist)

        # Sample doctors
        d1 = Doctor(
            full_name="Dr. Ananya Sharma",
            specialization="General Medicine",
            qualification="MBBS, MD",
            phone_number="9876543210",
            email="ananya@clinic.com",
            consultation_fee=500,
            available_timings="Mon-Fri 09:00-17:00",
        )
        d2 = Doctor(
            full_name="Dr. Rohan Mehta",
            specialization="Cardiology",
            qualification="MBBS, DM Cardiology",
            phone_number="9876543211",
            email="rohan@clinic.com",
            consultation_fee=1200,
            available_timings="Mon-Sat 10:00-14:00",
        )
        db.add(d1)
        db.add(d2)
        db.flush()

        # Doctor user linked to first doctor
        doctor_user = User(
            email="doctor@clinic.com",
            hashed_password=get_password_hash("doctor123"),
            full_name="Dr. Ananya Sharma",
            role=UserRole.DOCTOR,
            doctor_id=d1.id,
        )
        db.add(doctor_user)

        # Sample patients
        p1 = Patient(
            full_name="Rahul Verma",
            age=34,
            gender="Male",
            phone_number="9123456780",
            address="12 MG Road, Delhi",
            blood_group="B+",
            emergency_contact="9123456781",
            email="rahul@example.com",
        )
        p2 = Patient(
            full_name="Priya Singh",
            age=28,
            gender="Female",
            phone_number="9123456782",
            address="45 Park Street, Mumbai",
            blood_group="O+",
            emergency_contact="9123456783",
            email="priya@example.com",
        )
        db.add(p1)
        db.add(p2)

        db.commit()
        print("Seed completed successfully.")
        print("  Admin:        admin@clinic.com / admin123")
        print("  Receptionist: reception@clinic.com / reception123")
        print("  Doctor:       doctor@clinic.com / doctor123")
    except Exception as e:
        db.rollback()
        print(f"Seed error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
