from datetime import date
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.appointment import Appointment, AppointmentStatus
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.user import UserRole
from app.repositories import appointment as appointment_repository
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.utils.helpers import generate_appointment_number


ALLOWED_STATUS_TRANSITIONS = {
    AppointmentStatus.SCHEDULED: {
        AppointmentStatus.CONFIRMED,
        AppointmentStatus.CANCELLED,
        AppointmentStatus.NO_SHOW,
    },
    AppointmentStatus.CONFIRMED: {
        AppointmentStatus.COMPLETED,
        AppointmentStatus.CANCELLED,
        AppointmentStatus.NO_SHOW,
    },
    AppointmentStatus.COMPLETED: set(),
    AppointmentStatus.CANCELLED: set(),
    AppointmentStatus.NO_SHOW: set(),
}


def normalize_date(value) -> date:
    """
    Convert an appointment date into a Python date object.
    """

    if isinstance(value, date):
        return value

    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid appointment date. Use YYYY-MM-DD.",
            )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid appointment date.",
    )


def date_for_db(value) -> str:
    """
    PostgreSQL currently stores appointment_date as VARCHAR.

    Store dates in ISO format:
    YYYY-MM-DD
    """

    return normalize_date(value).isoformat()


def get_appointment(
    db: Session,
    appointment_id: int,
) -> Appointment:
    """
    Get an appointment by ID.
    """

    appointment = appointment_repository.get_by_id(
        db,
        appointment_id,
    )

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )

    return appointment


def check_double_booking(
    db: Session,
    doctor_id: int,
    appointment_date,
    time_slot: str,
    exclude_id: Optional[int] = None,
):
    """
    Check whether the doctor already has an active
    appointment for the selected date and time slot.
    """

    appointment_date_db = date_for_db(
        appointment_date
    )

    return appointment_repository.find_conflict(
        db=db,
        doctor_id=doctor_id,
        appointment_date=appointment_date_db,
        time_slot=time_slot,
        exclude_id=exclude_id,
    )


def create_appointment(
    db: Session,
    appointment_in: AppointmentCreate,
) -> Appointment:
    """
    Create a new appointment.
    """

    appointment_date = normalize_date(
        appointment_in.appointment_date
    )

    if appointment_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment date cannot be in the past",
        )

    patient = (
        db.query(Patient)
        .filter(
            Patient.id == appointment_in.patient_id
        )
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    doctor = (
        db.query(Doctor)
        .filter(
            Doctor.id == appointment_in.doctor_id,
            Doctor.is_active.is_(True),
        )
        .first()
    )

    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found or inactive",
        )

    existing = check_double_booking(
        db=db,
        doctor_id=appointment_in.doctor_id,
        appointment_date=appointment_date,
        time_slot=appointment_in.time_slot,
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "This time slot is already booked "
                "for the selected doctor"
            ),
        )

    appointment = Appointment(
        appointment_number=generate_appointment_number(),
        patient_id=appointment_in.patient_id,
        doctor_id=appointment_in.doctor_id,
        appointment_date=date_for_db(
            appointment_date
        ),
        time_slot=appointment_in.time_slot,
        reason_for_visit=(
            appointment_in.reason_for_visit
        ),
        status=AppointmentStatus.SCHEDULED,
    )

    try:
        appointment = appointment_repository.create(
            db,
            appointment,
        )

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "This time slot is already booked "
                "for the selected doctor"
            ),
        )

    return get_appointment(
        db,
        appointment.id,
    )


def list_appointments(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    status_filter: Optional[AppointmentStatus] = None,
    doctor_id: Optional[int] = None,
    patient_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    search: Optional[str] = None,
    current_user=None,
):
    """
    Return appointments with filtering and pagination.
    """

    if date_from and date_to and date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="date_from cannot be later than date_to",
        )

    # Doctors can only view their own appointments.
    if (
        current_user
        and current_user.role == UserRole.DOCTOR
    ):
        if not current_user.doctor_id:
            return []

        doctor_id = current_user.doctor_id

    return appointment_repository.list_all(
        db=db,
        skip=skip,
        limit=limit,
        status_filter=status_filter,
        doctor_id=doctor_id,
        patient_id=patient_id,
        date_from=date_from,
        date_to=date_to,
        search=search,
    )


def update_appointment(
    db: Session,
    appointment_id: int,
    appointment_in: AppointmentUpdate,
) -> Appointment:
    """
    Update an appointment.
    """

    appointment = (
        db.query(Appointment)
        .filter(
            Appointment.id == appointment_id
        )
        .first()
    )

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )

    data = appointment_in.model_dump(
        exclude_unset=True
    )

    if "appointment_date" in data:
        normalized_date = normalize_date(
            data["appointment_date"]
        )

        if normalized_date < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Appointment date cannot be "
                    "in the past"
                ),
            )

        data["appointment_date"] = date_for_db(
            normalized_date
        )

    old_status = appointment.status

    new_status = data.get(
        "status",
        appointment.status,
    )

    if new_status != old_status:

        allowed = ALLOWED_STATUS_TRANSITIONS.get(
            old_status,
            set(),
        )

        if new_status not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Cannot change appointment status "
                    f"from '{old_status.value}' to "
                    f"'{new_status.value}'"
                ),
            )

    if "appointment_date" in data:
        new_date = normalize_date(
            data["appointment_date"]
        )
    else:
        new_date = normalize_date(
            appointment.appointment_date
        )

    new_time_slot = data.get(
        "time_slot",
        appointment.time_slot,
    )

    if (
        "appointment_date" in data
        or "time_slot" in data
    ):
        conflict = check_double_booking(
            db=db,
            doctor_id=appointment.doctor_id,
            appointment_date=new_date,
            time_slot=new_time_slot,
            exclude_id=appointment_id,
        )

        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "This time slot is already booked "
                    "for the selected doctor"
                ),
            )

    for key, value in data.items():
        setattr(
            appointment,
            key,
            value,
        )

    try:
        appointment = appointment_repository.update(
            db,
            appointment,
        )

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "This time slot is already booked "
                "for the selected doctor"
            ),
        )

    return get_appointment(
        db,
        appointment.id,
    )


def cancel_appointment(
    db: Session,
    appointment_id: int,
) -> None:
    """
    Cancel an appointment.
    """

    appointment = (
        db.query(Appointment)
        .filter(
            Appointment.id == appointment_id
        )
        .first()
    )

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )

    if appointment.status in (
        AppointmentStatus.COMPLETED,
        AppointmentStatus.CANCELLED,
        AppointmentStatus.NO_SHOW,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Cannot cancel an appointment with "
                f"status '{appointment.status.value}'"
            ),
        )

    appointment.status = AppointmentStatus.CANCELLED

    appointment_repository.update(
        db,
        appointment,
    )

    return None