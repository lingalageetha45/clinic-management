from typing import Optional

from sqlalchemy.orm import Session

from app.models.patient import Patient


def get_patient(
    db: Session,
    patient_id: int,
) -> Optional[Patient]:
    return (
        db.query(Patient)
        .filter(Patient.id == patient_id)
        .first()
    )


def get_patient_by_phone(
    db: Session,
    phone_number: str,
) -> Optional[Patient]:
    return (
        db.query(Patient)
        .filter(Patient.phone_number == phone_number)
        .first()
    )


def get_patients(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
):
    query = db.query(Patient)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Patient.full_name.ilike(search_term))
            | (Patient.phone_number.ilike(search_term))
        )

    return (
        query
        .order_by(Patient.full_name)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_patient(
    db: Session,
    patient_data: dict,
) -> Patient:
    patient = Patient(**patient_data)

    db.add(patient)
    db.commit()
    db.refresh(patient)

    return patient


def update_patient(
    db: Session,
    patient: Patient,
    patient_data: dict,
) -> Patient:
    for key, value in patient_data.items():
        setattr(patient, key, value)

    db.commit()
    db.refresh(patient)

    return patient


def delete_patient(
    db: Session,
    patient: Patient,
) -> None:
    db.delete(patient)
    db.commit()