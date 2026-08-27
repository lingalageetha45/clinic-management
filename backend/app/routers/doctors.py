from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user, require_roles
from app.core.database import get_db
from app.models.user import User, UserRole
from app.schemas.doctor import DoctorCreate, DoctorOut, DoctorUpdate
from app.services import doctor as doctor_service


router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"],
)


@router.post(
    "",
    response_model=DoctorOut,
    status_code=status.HTTP_201_CREATED,
)
def create_doctor(
    doctor_in: DoctorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN)
    ),
):
    return doctor_service.create_doctor(
        db,
        doctor_in,
    )


@router.get(
    "",
    response_model=List[DoctorOut],
)
def list_doctors(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    specialization: Optional[str] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return doctor_service.list_doctors(
        db,
        skip=skip,
        limit=limit,
        specialization=specialization,
        search=search,
        is_active=is_active,
    )


@router.get(
    "/{doctor_id}",
    response_model=DoctorOut,
)
def get_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return doctor_service.get_doctor(
        db,
        doctor_id,
    )


@router.put(
    "/{doctor_id}",
    response_model=DoctorOut,
)
def update_doctor(
    doctor_id: int,
    doctor_in: DoctorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN)
    ),
):
    return doctor_service.update_doctor(
        db,
        doctor_id,
        doctor_in,
    )


@router.delete(
    "/{doctor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN)
    ),
):
    doctor_service.delete_doctor(
        db,
        doctor_id,
    )

    return None