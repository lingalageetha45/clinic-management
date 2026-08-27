from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.prescription import Prescription
from app.models.user import User, UserRole
from app.repositories import prescription as prescription_repository
from app.schemas.prescription import (
    PrescriptionCreate,
    PrescriptionUpdate,
)


def create_prescription(
    db: Session,
    prescription_in: PrescriptionCreate,
    current_user: User,
) -> Prescription:
    patient = (
        db.query(Patient)
        .filter(Patient.id == prescription_in.patient_id)
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    doctor = (
        db.query(Doctor)
        .filter(Doctor.id == prescription_in.doctor_id)
        .first()
    )

    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )

    if current_user.role == UserRole.DOCTOR:
        if current_user.doctor_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Doctor account is not linked to a doctor profile",
            )

        if prescription_in.doctor_id != current_user.doctor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only create prescriptions for yourself",
            )

    prescription = Prescription(
        **prescription_in.model_dump()
    )

    return prescription_repository.create(
        db,
        prescription,
    )


def get_prescription(
    db: Session,
    prescription_id: int,
    current_user: User,
) -> Prescription:
    prescription = prescription_repository.get_by_id(
        db,
        prescription_id,
    )

    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found",
        )

    if current_user.role == UserRole.DOCTOR:
        if current_user.doctor_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Doctor account is not linked to a doctor profile",
            )

        if prescription.doctor_id != current_user.doctor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

    return prescription


def list_prescriptions(
    db: Session,
    current_user: User,
    skip: int = 0,
    limit: int = 50,
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
) -> List[Prescription]:
    if current_user.role == UserRole.DOCTOR:
        if current_user.doctor_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Doctor account is not linked to a doctor profile",
            )

        doctor_id = current_user.doctor_id

    return prescription_repository.list_all(
        db=db,
        skip=skip,
        limit=limit,
        patient_id=patient_id,
        doctor_id=doctor_id,
    )


def update_prescription(
    db: Session,
    prescription_id: int,
    prescription_in: PrescriptionUpdate,
    current_user: User,
) -> Prescription:
    prescription = prescription_repository.get_by_id(
        db,
        prescription_id,
    )

    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found",
        )

    if current_user.role == UserRole.DOCTOR:
        if current_user.doctor_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Doctor account is not linked to a doctor profile",
            )

        if prescription.doctor_id != current_user.doctor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not your prescription",
            )

    data = prescription_in.model_dump(
        exclude_unset=True
    )

    return prescription_repository.update(
        db=db,
        prescription=prescription,
        data=data,
    )