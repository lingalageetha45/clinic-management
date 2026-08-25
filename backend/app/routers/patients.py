from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.models.patient import Patient
from app.models.user import User, UserRole
from app.schemas.patient import PatientCreate, PatientUpdate, PatientOut
from app.auth.deps import get_current_user, require_roles


router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post(
    "",
    response_model=PatientOut,
    status_code=status.HTTP_201_CREATED,
)
def create_patient(
    patient_in: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST)
    ),
):
    existing = (
        db.query(Patient)
        .filter(Patient.phone_number == patient_in.phone_number)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient with this phone number already exists",
        )

    patient = Patient(**patient_in.model_dump())

    db.add(patient)
    db.commit()
    db.refresh(patient)

    return patient


@router.get("", response_model=List[PatientOut])
def list_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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


@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id)
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    return patient


@router.put("/{patient_id}", response_model=PatientOut)
def update_patient(
    patient_id: int,
    patient_in: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST)
    ),
):
    patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id)
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    data = patient_in.model_dump(exclude_unset=True)

    if "phone_number" in data:
        existing = (
            db.query(Patient)
            .filter(
                Patient.phone_number == data["phone_number"],
                Patient.id != patient_id,
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Patient with this phone number already exists",
            )

    for key, value in data.items():
        setattr(patient, key, value)

    db.commit()
    db.refresh(patient)

    return patient


@router.delete(
    "/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN)
    ),
):
    patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id)
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    db.delete(patient)
    db.commit()

    return None