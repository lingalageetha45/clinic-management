from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.medical_record import MedicalRecord


def get_by_id(
    db: Session,
    record_id: int,
) -> Optional[MedicalRecord]:
    return (
        db.query(MedicalRecord)
        .filter(MedicalRecord.id == record_id)
        .first()
    )


def get_by_patient(
    db: Session,
    patient_id: int,
) -> List[MedicalRecord]:
    return (
        db.query(MedicalRecord)
        .filter(MedicalRecord.patient_id == patient_id)
        .order_by(MedicalRecord.created_at.desc())
        .all()
    )


def create(
    db: Session,
    patient_id: int,
    uploaded_by: Optional[int],
    file_name: str,
    original_name: str,
    file_type: str,
    file_path: str,
    description: Optional[str] = None,
) -> MedicalRecord:
    record = MedicalRecord(
        patient_id=patient_id,
        uploaded_by=uploaded_by,
        file_name=file_name,
        original_name=original_name,
        file_type=file_type,
        file_path=file_path,
        description=description,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


def delete(
    db: Session,
    record: MedicalRecord,
) -> None:
    db.delete(record)
    db.commit()