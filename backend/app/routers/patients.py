from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user, require_roles
from app.core.database import get_db
from app.models.user import User, UserRole
from app.schemas.patient import PatientCreate, PatientOut, PatientUpdate
from app.services import patient as patient_service


router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
)


@router.post(
    "",
    response_model=PatientOut,
    status_code=status.HTTP_201_CREATED,
)
def create_patient(
    patient_in: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.RECEPTIONIST,
        )
    ),
):
    return patient_service.create_patient(
        db,
        patient_in,
    )


@router.get(
    "",
    response_model=List[PatientOut],
)
def list_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return patient_service.list_patients(
        db,
        skip=skip,
        limit=limit,
        search=search,
    )


@router.get(
    "/{patient_id}",
    response_model=PatientOut,
)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return patient_service.get_patient(
        db,
        patient_id,
    )


@router.put(
    "/{patient_id}",
    response_model=PatientOut,
)
def update_patient(
    patient_id: int,
    patient_in: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.RECEPTIONIST,
        )
    ),
):
    return patient_service.update_patient(
        db,
        patient_id,
        patient_in,
    )


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
    patient_service.delete_patient(
        db,
        patient_id,
    )

    return None