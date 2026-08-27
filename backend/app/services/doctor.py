from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.doctor import Doctor
from app.repositories import doctor as doctor_repository
from app.schemas.doctor import DoctorCreate, DoctorUpdate


def create_doctor(
    db: Session,
    doctor_in: DoctorCreate,
) -> Doctor:
    existing = doctor_repository.get_doctor_by_email(
        db,
        doctor_in.email,
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor with this email already exists",
        )

    return doctor_repository.create_doctor(
        db,
        doctor_in.model_dump(),
    )


def get_doctor(
    db: Session,
    doctor_id: int,
) -> Doctor:
    doctor = doctor_repository.get_doctor(
        db,
        doctor_id,
    )

    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )

    return doctor


def list_doctors(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    specialization: Optional[str] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = True,
):
    return doctor_repository.get_doctors(
        db,
        skip=skip,
        limit=limit,
        specialization=specialization,
        search=search,
        is_active=is_active,
    )


def update_doctor(
    db: Session,
    doctor_id: int,
    doctor_in: DoctorUpdate,
) -> Doctor:
    doctor = doctor_repository.get_doctor(
        db,
        doctor_id,
    )

    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )

    data = doctor_in.model_dump(exclude_unset=True)

    if "email" in data:
        existing = doctor_repository.get_doctor_by_email(
            db,
            data["email"],
        )

        if existing and existing.id != doctor_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Doctor with this email already exists",
            )

    return doctor_repository.update_doctor(
        db,
        doctor,
        data,
    )


def delete_doctor(
    db: Session,
    doctor_id: int,
) -> None:
    doctor = doctor_repository.get_doctor(
        db,
        doctor_id,
    )

    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )

    # Keep the existing soft-delete behavior.
    doctor_repository.deactivate_doctor(
        db,
        doctor,
    )