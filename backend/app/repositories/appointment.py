from datetime import date
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.models.appointment import Appointment, AppointmentStatus


def get_by_id(
    db: Session,
    appointment_id: int,
) -> Optional[Appointment]:
    return (
        db.query(Appointment)
        .options(
            joinedload(Appointment.patient),
            joinedload(Appointment.doctor),
        )
        .filter(Appointment.id == appointment_id)
        .first()
    )


def get_by_number(
    db: Session,
    appointment_number: str,
) -> Optional[Appointment]:
    return (
        db.query(Appointment)
        .filter(
            Appointment.appointment_number
            == appointment_number
        )
        .first()
    )


def find_conflict(
    db: Session,
    doctor_id: int,
    appointment_date: str,
    time_slot: str,
    exclude_id: Optional[int] = None,
) -> Optional[Appointment]:

    query = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date == appointment_date,
        Appointment.time_slot == time_slot,
        Appointment.status.notin_(
            [
                AppointmentStatus.CANCELLED,
                AppointmentStatus.NO_SHOW,
            ]
        ),
    )

    if exclude_id is not None:
        query = query.filter(
            Appointment.id != exclude_id
        )

    return query.first()


def create(
    db: Session,
    appointment: Appointment,
) -> Appointment:

    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return appointment


def update(
    db: Session,
    appointment: Appointment,
) -> Appointment:

    db.commit()
    db.refresh(appointment)

    return appointment


def delete(
    db: Session,
    appointment: Appointment,
) -> None:

    db.delete(appointment)
    db.commit()


def list_all(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    status_filter: Optional[AppointmentStatus] = None,
    doctor_id: Optional[int] = None,
    patient_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    search: Optional[str] = None,
):
    query = (
        db.query(Appointment)
        .options(
            joinedload(Appointment.patient),
            joinedload(Appointment.doctor),
        )
    )

    if status_filter:
        query = query.filter(
            Appointment.status == status_filter
        )

    if doctor_id:
        query = query.filter(
            Appointment.doctor_id == doctor_id
        )

    if patient_id:
        query = query.filter(
            Appointment.patient_id == patient_id
        )

    if date_from:
        query = query.filter(
            Appointment.appointment_date
            >= date_from.isoformat()
        )

    if date_to:
        query = query.filter(
            Appointment.appointment_date
            <= date_to.isoformat()
        )

    if search:
        search_term = f"%{search}%"

        query = query.filter(
            Appointment.appointment_number.ilike(
                search_term
            )
        )

    return (
        query
        .order_by(
            Appointment.appointment_date.desc(),
            Appointment.time_slot,
        )
        .offset(skip)
        .limit(limit)
        .all()
    )