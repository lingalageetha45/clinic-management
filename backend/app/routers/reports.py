from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import date

from app.core.database import get_db
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.appointment import Appointment, AppointmentStatus
from app.models.user import User, UserRole
from app.schemas.report import DashboardStats
from app.auth.deps import get_current_user, require_roles

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/dashboard", response_model=DashboardStats)
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST)),
):
    today = date.today().isoformat()

    total_patients = db.query(func.count(Patient.id)).scalar() or 0
    total_doctors = db.query(func.count(Doctor.id)).filter(Doctor.is_active == True).scalar() or 0

    todays = (
        db.query(func.count(Appointment.id))
        .filter(Appointment.appointment_date == today)
        .filter(Appointment.status.notin_([AppointmentStatus.CANCELLED]))
        .scalar()
        or 0
    )

    upcoming = (
        db.query(func.count(Appointment.id))
        .filter(Appointment.appointment_date >= today)
        .filter(Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]))
        .scalar()
        or 0
    )

    completed = (
        db.query(func.count(Appointment.id))
        .filter(Appointment.status == AppointmentStatus.COMPLETED)
        .scalar()
        or 0
    )

    cancelled = (
        db.query(func.count(Appointment.id))
        .filter(Appointment.status == AppointmentStatus.CANCELLED)
        .scalar()
        or 0
    )

    # Most visited doctor
    most_visited = (
        db.query(Doctor.full_name, func.count(Appointment.id).label("cnt"))
        .join(Appointment, Appointment.doctor_id == Doctor.id)
        .filter(Appointment.status != AppointmentStatus.CANCELLED)
        .group_by(Doctor.id, Doctor.full_name)
        .order_by(desc("cnt"))
        .first()
    )
    most_visited_name = most_visited[0] if most_visited else None

    # Average daily appointments (last 30 days approximation using total / distinct dates)
    total_appts = db.query(func.count(Appointment.id)).scalar() or 0
    distinct_days = (
        db.query(func.count(func.distinct(Appointment.appointment_date))).scalar() or 1
    )
    avg_daily = round(total_appts / max(distinct_days, 1), 2)

    return DashboardStats(
        total_patients=total_patients,
        total_doctors=total_doctors,
        todays_appointments=todays,
        upcoming_appointments=upcoming,
        completed_appointments=completed,
        cancelled_appointments=cancelled,
        most_visited_doctor=most_visited_name,
        average_daily_appointments=avg_daily,
    )


@router.get("/appointments")
def appointments_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    by_status = (
        db.query(Appointment.status, func.count(Appointment.id))
        .group_by(Appointment.status)
        .all()
    )
    return {
        "by_status": {s.value if hasattr(s, "value") else str(s): c for s, c in by_status}
    }


@router.get("/doctors")
def doctors_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    data = (
        db.query(Doctor.full_name, Doctor.specialization, func.count(Appointment.id).label("appts"))
        .outerjoin(Appointment, Appointment.doctor_id == Doctor.id)
        .group_by(Doctor.id, Doctor.full_name, Doctor.specialization)
        .order_by(desc("appts"))
        .all()
    )
    return [
        {"doctor": name, "specialization": spec, "appointment_count": cnt}
        for name, spec, cnt in data
    ]
