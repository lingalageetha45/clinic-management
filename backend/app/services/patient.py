from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.repositories import patient as patient_repository
from app.schemas.patient import PatientCreate, PatientUpdate


def create_patient(
    db: Session,
    patient_in: PatientCreate,
) -> Patient:
    existing = patient_repository.get_patient_by_phone(
        db,
        patient_in.phone_number,
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient with this phone number already exists",
        )

    return patient_repository.create_patient(
        db,
        patient_in.model_dump(),
    )


def get_patient(
    db: Session,
    patient_id: int,
) -> Patient:
    patient = patient_repository.get_patient(
        db,
        patient_id,
    )

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    return patient


def list_patients(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
):
    return patient_repository.get_patients(
        db,
        skip=skip,
        limit=limit,
        search=search,
    )


def update_patient(
    db: Session,
    patient_id: int,
    patient_in: PatientUpdate,
) -> Patient:
    patient = patient_repository.get_patient(
        db,
        patient_id,
    )

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    data = patient_in.model_dump(exclude_unset=True)

    if "phone_number" in data:
        existing = patient_repository.get_patient_by_phone(
            db,
            data["phone_number"],
        )

        if existing and existing.id != patient_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Patient with this phone number already exists",
            )

    return patient_repository.update_patient(
        db,
        patient,
        data,
    )


def delete_patient(
    db: Session,
    patient_id: int,
) -> None:
    patient = patient_repository.get_patient(
        db,
        patient_id,
    )

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    patient_repository.delete_patient(
        db,
        patient,
    )