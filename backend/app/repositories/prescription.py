from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.models.prescription import Prescription


def get_by_id(
    db: Session,
    prescription_id: int,
) -> Optional[Prescription]:
    return (
        db.query(Prescription)
        .options(
            joinedload(Prescription.patient),
            joinedload(Prescription.doctor),
        )
        .filter(Prescription.id == prescription_id)
        .first()
    )


def list_all(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
) -> List[Prescription]:
    query = (
        db.query(Prescription)
        .options(
            joinedload(Prescription.patient),
            joinedload(Prescription.doctor),
        )
    )

    if patient_id is not None:
        query = query.filter(
            Prescription.patient_id == patient_id
        )

    if doctor_id is not None:
        query = query.filter(
            Prescription.doctor_id == doctor_id
        )

    return (
        query
        .order_by(Prescription.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create(
    db: Session,
    prescription: Prescription,
) -> Prescription:
    db.add(prescription)
    db.commit()
    db.refresh(prescription)

    return prescription


def update(
    db: Session,
    prescription: Prescription,
    data: dict,
) -> Prescription:
    for key, value in data.items():
        setattr(prescription, key, value)

    db.commit()
    db.refresh(prescription)

    return prescription