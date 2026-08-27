from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.medical_record import MedicalRecord
from app.repositories import medical_record as medical_record_repository


def get_medical_record(
    db: Session,
    record_id: int,
) -> MedicalRecord:
    record = medical_record_repository.get_by_id(
        db,
        record_id,
    )

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found",
        )

    return record


def list_patient_records(
    db: Session,
    patient_id: int,
) -> List[MedicalRecord]:
    return medical_record_repository.get_by_patient(
        db,
        patient_id,
    )


def create_medical_record(
    db: Session,
    patient_id: int,
    uploaded_by: Optional[int],
    file_name: str,
    original_name: str,
    file_type: str,
    file_path: str,
    description: Optional[str] = None,
) -> MedicalRecord:
    return medical_record_repository.create(
        db=db,
        patient_id=patient_id,
        uploaded_by=uploaded_by,
        file_name=file_name,
        original_name=original_name,
        file_type=file_type,
        file_path=file_path,
        description=description,
    )


def delete_medical_record(
    db: Session,
    record_id: int,
) -> None:
    record = get_medical_record(
        db,
        record_id,
    )

    medical_record_repository.delete(
        db,
        record,
    )