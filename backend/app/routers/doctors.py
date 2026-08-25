from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.models.doctor import Doctor
from app.models.user import User, UserRole
from app.schemas.doctor import DoctorCreate, DoctorUpdate, DoctorOut
from app.auth.deps import get_current_user, require_roles


router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.post(
    "",
    response_model=DoctorOut,
    status_code=status.HTTP_201_CREATED,
)
def create_doctor(
    doctor_in: DoctorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    existing = (
        db.query(Doctor)
        .filter(Doctor.email == doctor_in.email)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor with this email already exists",
        )

    doctor = Doctor(**doctor_in.model_dump())

    db.add(doctor)
    db.commit()
    db.refresh(doctor)

    return doctor


@router.get("", response_model=List[DoctorOut])
def list_doctors(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    specialization: Optional[str] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Doctor)

    if is_active is not None:
        query = query.filter(
            Doctor.is_active.is_(is_active)
        )

    if specialization:
        query = query.filter(
            Doctor.specialization.ilike(f"%{specialization}%")
        )

    if search:
        query = query.filter(
            (Doctor.full_name.ilike(f"%{search}%"))
            | (Doctor.email.ilike(f"%{search}%"))
        )

    return (
        query
        .order_by(Doctor.full_name)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{doctor_id}", response_model=DoctorOut)
def get_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doctor = (
        db.query(Doctor)
        .filter(Doctor.id == doctor_id)
        .first()
    )

    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )

    return doctor


@router.put("/{doctor_id}", response_model=DoctorOut)
def update_doctor(
    doctor_id: int,
    doctor_in: DoctorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    doctor = (
        db.query(Doctor)
        .filter(Doctor.id == doctor_id)
        .first()
    )

    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )

    data = doctor_in.model_dump(exclude_unset=True)

    if "email" in data:
        existing = (
            db.query(Doctor)
            .filter(
                Doctor.email == data["email"],
                Doctor.id != doctor_id,
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Doctor with this email already exists",
            )

    for key, value in data.items():
        setattr(doctor, key, value)

    db.commit()
    db.refresh(doctor)

    return doctor


@router.delete(
    "/{doctor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    doctor = (
        db.query(Doctor)
        .filter(Doctor.id == doctor_id)
        .first()
    )

    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )

    # Soft delete
    doctor.is_active = False

    db.commit()

    return None