from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List

from app.core.database import get_db
from app.models.prescription import Prescription
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.user import User, UserRole
from app.schemas.prescription import (
    PrescriptionCreate,
    PrescriptionUpdate,
    PrescriptionOut,
)
from app.auth.deps import get_current_user, require_roles
from app.utils.email import send_email, prescription_created_email

router = APIRouter(prefix="/prescriptions", tags=["Prescriptions"])


@router.post(
    "",
    response_model=PrescriptionOut,
    status_code=status.HTTP_201_CREATED,
)
def create_prescription(
    presc_in: PrescriptionCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.DOCTOR)
    ),
):
    patient = (
        db.query(Patient)
        .filter(Patient.id == presc_in.patient_id)
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    doctor = (
        db.query(Doctor)
        .filter(Doctor.id == presc_in.doctor_id)
        .first()
    )

    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )

    # Doctors can only create prescriptions for themselves.
    if current_user.role == UserRole.DOCTOR:
        if current_user.doctor_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Doctor account is not linked to a doctor profile",
            )

        if presc_in.doctor_id != current_user.doctor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only create prescriptions for yourself",
            )

    presc = Prescription(**presc_in.model_dump())

    db.add(presc)
    db.commit()
    db.refresh(presc)

    # Send prescription notification in the background.
    subject, body = prescription_created_email(
        patient.full_name,
        doctor.full_name,
        presc.diagnosis,
    )

    email_to = patient.email or "patient@example.com"

    background_tasks.add_task(
        send_email,
        email_to,
        subject,
        body,
    )

    # Reload with related patient and doctor information.
    presc = (
        db.query(Prescription)
        .options(
            joinedload(Prescription.patient),
            joinedload(Prescription.doctor),
        )
        .filter(Prescription.id == presc.id)
        .first()
    )

    return presc


@router.get("", response_model=List[PrescriptionOut])
def list_prescriptions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = (
        db.query(Prescription)
        .options(
            joinedload(Prescription.patient),
            joinedload(Prescription.doctor),
        )
    )

    # Doctors can only see their own prescriptions.
    if current_user.role == UserRole.DOCTOR:
        if current_user.doctor_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Doctor account is not linked to a doctor profile",
            )

        q = q.filter(
            Prescription.doctor_id == current_user.doctor_id
        )

    if patient_id is not None:
        q = q.filter(Prescription.patient_id == patient_id)

    if doctor_id is not None:
        q = q.filter(Prescription.doctor_id == doctor_id)

    return (
        q.order_by(Prescription.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get(
    "/{prescription_id}",
    response_model=PrescriptionOut,
)
def get_prescription(
    prescription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    presc = (
        db.query(Prescription)
        .options(
            joinedload(Prescription.patient),
            joinedload(Prescription.doctor),
        )
        .filter(Prescription.id == prescription_id)
        .first()
    )

    if not presc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found",
        )

    # Doctors can only view their own prescriptions.
    if current_user.role == UserRole.DOCTOR:
        if current_user.doctor_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Doctor account is not linked to a doctor profile",
            )

        if presc.doctor_id != current_user.doctor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

    return presc


@router.put(
    "/{prescription_id}",
    response_model=PrescriptionOut,
)
def update_prescription(
    prescription_id: int,
    presc_in: PrescriptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.DOCTOR)
    ),
):
    presc = (
        db.query(Prescription)
        .filter(Prescription.id == prescription_id)
        .first()
    )

    if not presc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found",
        )

    # Doctors can only update their own prescriptions.
    if current_user.role == UserRole.DOCTOR:
        if current_user.doctor_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Doctor account is not linked to a doctor profile",
            )

        if presc.doctor_id != current_user.doctor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not your prescription",
            )

    data = presc_in.model_dump(exclude_unset=True)

    for key, value in data.items():
        setattr(presc, key, value)

    db.commit()
    db.refresh(presc)

    # Reload with related patient and doctor information.
    presc = (
        db.query(Prescription)
        .options(
            joinedload(Prescription.patient),
            joinedload(Prescription.doctor),
        )
        .filter(Prescription.id == presc.id)
        .first()
    )

    return presc