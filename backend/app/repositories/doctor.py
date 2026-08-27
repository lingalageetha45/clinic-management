from typing import Optional

from sqlalchemy.orm import Session

from app.models.doctor import Doctor


def get_doctor(
    db: Session,
    doctor_id: int,
) -> Optional[Doctor]:
    return (
        db.query(Doctor)
        .filter(Doctor.id == doctor_id)
        .first()
    )


def get_doctor_by_email(
    db: Session,
    email: str,
) -> Optional[Doctor]:
    return (
        db.query(Doctor)
        .filter(Doctor.email == email)
        .first()
    )


def get_doctors(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    specialization: Optional[str] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = True,
):
    query = db.query(Doctor)

    if is_active is not None:
        query = query.filter(
            Doctor.is_active.is_(is_active)
        )

    if specialization:
        query = query.filter(
            Doctor.specialization.ilike(
                f"%{specialization}%"
            )
        )

    if search:
        search_term = f"%{search}%"

        query = query.filter(
            (Doctor.full_name.ilike(search_term))
            | (Doctor.email.ilike(search_term))
        )

    return (
        query
        .order_by(Doctor.full_name)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_doctor(
    db: Session,
    doctor_data: dict,
) -> Doctor:
    doctor = Doctor(**doctor_data)

    db.add(doctor)
    db.commit()
    db.refresh(doctor)

    return doctor


def update_doctor(
    db: Session,
    doctor: Doctor,
    doctor_data: dict,
) -> Doctor:
    for key, value in doctor_data.items():
        setattr(doctor, key, value)

    db.commit()
    db.refresh(doctor)

    return doctor


def deactivate_doctor(
    db: Session,
    doctor: Doctor,
) -> None:
    doctor.is_active = False

    db.commit()