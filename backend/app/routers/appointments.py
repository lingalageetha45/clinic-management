from datetime import date
from typing import List, Optional
import csv
import io

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.auth.deps import get_current_user, require_roles
from app.core.database import get_db
from app.models.appointment import Appointment, AppointmentStatus
from app.models.audit_log import AuditLog
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.user import User, UserRole
from app.schemas.appointment import AppointmentCreate, AppointmentOut, AppointmentUpdate
from app.utils.email import (
    appointment_confirmation_email,
    appointment_reminder_email,
    send_email,
)
from app.utils.helpers import generate_appointment_number


router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"],
)


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


def _log_audit(
    db: Session,
    user_id: int,
    action: str,
    entity_id: int,
    old_val: str = None,
    new_val: str = None,
    details: str = None,
):
    log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type="appointment",
        entity_id=entity_id,
        old_value=old_val,
        new_value=new_val,
        details=details,
    )

    db.add(log)


def _get_appointment(
    db: Session,
    appointment_id: int,
) -> Appointment:
    appointment = (
        db.query(Appointment)
        .options(
            joinedload(Appointment.patient),
            joinedload(Appointment.doctor),
        )
        .filter(Appointment.id == appointment_id)
        .first()
    )

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )

    return appointment


def _normalize_date(value) -> date:
    """
    Convert an appointment date into a Python date object.

    Handles:
    - datetime.date
    - ISO date string: YYYY-MM-DD
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


def _date_for_db(value) -> str:
    """
    PostgreSQL currently stores appointment_date as VARCHAR.

    Convert the Python date into ISO format so PostgreSQL compares:
    VARCHAR = VARCHAR
    instead of:
    VARCHAR = DATE
    """
    normalized = _normalize_date(value)
    return normalized.isoformat()


def _check_double_booking(
    db: Session,
    doctor_id: int,
    appointment_date,
    time_slot: str,
    exclude_id: Optional[int] = None,
):
    appointment_date_db = _date_for_db(appointment_date)

    query = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date == appointment_date_db,
        Appointment.time_slot == time_slot,
        Appointment.status.notin_(
            [
                AppointmentStatus.CANCELLED,
                AppointmentStatus.NO_SHOW,
            ]
        ),
    )

    if exclude_id is not None:
        query = query.filter(Appointment.id != exclude_id)

    return query.first()


@router.post(
    "",
    response_model=AppointmentOut,
    status_code=status.HTTP_201_CREATED,
)
def create_appointment(
    appt_in: AppointmentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST)
    ),
):
    appointment_date = _normalize_date(appt_in.appointment_date)

    if appointment_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment date cannot be in the past",
        )

    patient = (
        db.query(Patient)
        .filter(Patient.id == appt_in.patient_id)
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
            Doctor.id == appt_in.doctor_id,
            Doctor.is_active.is_(True),
        )
        .first()
    )

    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found or inactive",
        )

    existing = _check_double_booking(
        db=db,
        doctor_id=appt_in.doctor_id,
        appointment_date=appointment_date,
        time_slot=appt_in.time_slot,
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This time slot is already booked for the selected doctor",
        )

    appointment = Appointment(
        appointment_number=generate_appointment_number(),
        patient_id=appt_in.patient_id,
        doctor_id=appt_in.doctor_id,
        appointment_date=_date_for_db(appointment_date),
        time_slot=appt_in.time_slot,
        reason_for_visit=appt_in.reason_for_visit,
        status=AppointmentStatus.SCHEDULED,
    )

    try:
        db.add(appointment)
        db.commit()
        db.refresh(appointment)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This time slot is already booked for the selected doctor",
        )

    subject, body = appointment_confirmation_email(
        patient.full_name,
        doctor.full_name,
        appointment.appointment_date,
        appointment.time_slot,
        appointment.appointment_number,
    )

    email_to = getattr(patient, "email", None)

    if email_to:
        background_tasks.add_task(
            send_email,
            email_to,
            subject,
            body,
        )

    return _get_appointment(db, appointment.id)


@router.get(
    "",
    response_model=List[AppointmentOut],
)
def list_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status_filter: Optional[AppointmentStatus] = Query(
        None,
        alias="status",
    ),
    doctor_id: Optional[int] = None,
    patient_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if date_from and date_to and date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="date_from cannot be later than date_to",
        )

    query = (
        db.query(Appointment)
        .options(
            joinedload(Appointment.patient),
            joinedload(Appointment.doctor),
        )
    )

    if current_user.role == UserRole.DOCTOR:
        if not current_user.doctor_id:
            return []

        query = query.filter(
            Appointment.doctor_id == current_user.doctor_id
        )

    if status_filter:
        query = query.filter(
            Appointment.status == status_filter
        )

    if doctor_id:
        query = query.filter(
            Appointment.doctor_id == doctor_id
        )

    if patient_id:
        query = query.filter(
            Appointment.patient_id == patient_id
        )

    if date_from:
        query = query.filter(
            Appointment.appointment_date >= date_from.isoformat()
        )

    if date_to:
        query = query.filter(
            Appointment.appointment_date <= date_to.isoformat()
        )

    if search:
        search_term = f"%{search}%"

        query = (
            query.join(Patient)
            .join(Doctor)
            .filter(
                (Appointment.appointment_number.ilike(search_term))
                | (Patient.full_name.ilike(search_term))
                | (Doctor.full_name.ilike(search_term))
            )
        )

    return (
        query
        .order_by(
            Appointment.appointment_date.desc(),
            Appointment.time_slot,
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/export/csv")
def export_appointments_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST)
    ),
):
    appointments = (
        db.query(Appointment)
        .options(
            joinedload(Appointment.patient),
            joinedload(Appointment.doctor),
        )
        .order_by(
            Appointment.appointment_date.desc(),
            Appointment.time_slot,
        )
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(
        [
            "Appointment Number",
            "Patient",
            "Doctor",
            "Date",
            "Time Slot",
            "Status",
            "Reason",
        ]
    )

    for appointment in appointments:
        writer.writerow(
            [
                appointment.appointment_number,
                appointment.patient.full_name
                if appointment.patient
                else "",
                appointment.doctor.full_name
                if appointment.doctor
                else "",
                appointment.appointment_date,
                appointment.time_slot,
                appointment.status.value,
                appointment.reason_for_visit or "",
            ]
        )

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=appointments.csv"
        },
    )


@router.get(
    "/{appointment_id}",
    response_model=AppointmentOut,
)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    appointment = _get_appointment(db, appointment_id)

    if current_user.role == UserRole.DOCTOR:
        if current_user.doctor_id != appointment.doctor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not your appointment",
            )

    return appointment


@router.put(
    "/{appointment_id}",
    response_model=AppointmentOut,
)
def update_appointment(
    appointment_id: int,
    appt_in: AppointmentUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    appointment = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id)
        .first()
    )

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )

    if current_user.role == UserRole.DOCTOR:
        if current_user.doctor_id != appointment.doctor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not your appointment",
            )

        if (
            appt_in.appointment_date is not None
            or appt_in.time_slot is not None
            or appt_in.reason_for_visit is not None
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Doctors can only update appointment status",
            )

    elif current_user.role not in (
        UserRole.ADMIN,
        UserRole.RECEPTIONIST,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    data = appt_in.model_dump(exclude_unset=True)

    if "appointment_date" in data:
        normalized_date = _normalize_date(
            data["appointment_date"]
        )
        data["appointment_date"] = _date_for_db(
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
        new_date = _normalize_date(
            data["appointment_date"]
        )
    else:
        new_date = _normalize_date(
            appointment.appointment_date
        )

    new_slot = data.get(
        "time_slot",
        appointment.time_slot,
    )

    if new_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment date cannot be in the past",
        )

    if (
        "appointment_date" in data
        or "time_slot" in data
    ):
        conflict = _check_double_booking(
            db=db,
            doctor_id=appointment.doctor_id,
            appointment_date=new_date,
            time_slot=new_slot,
            exclude_id=appointment_id,
        )

        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This time slot is already booked for the selected doctor",
            )

    for key, value in data.items():
        setattr(appointment, key, value)

    try:
        db.commit()
        db.refresh(appointment)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This time slot is already booked for the selected doctor",
        )

    _log_audit(
        db=db,
        user_id=current_user.id,
        action="update",
        entity_id=appointment.id,
        old_val=old_status.value,
        new_val=appointment.status.value,
        details=str(data),
    )

    db.commit()

    if (
        old_status != AppointmentStatus.CONFIRMED
        and appointment.status == AppointmentStatus.CONFIRMED
    ):
        patient = (
            db.query(Patient)
            .filter(Patient.id == appointment.patient_id)
            .first()
        )

        doctor = (
            db.query(Doctor)
            .filter(Doctor.id == appointment.doctor_id)
            .first()
        )

        if patient and doctor:
            subject, body = appointment_reminder_email(
                patient.full_name,
                doctor.full_name,
                appointment.appointment_date,
                appointment.time_slot,
                appointment.appointment_number,
            )

            email_to = getattr(patient, "email", None)

            if email_to:
                background_tasks.add_task(
                    send_email,
                    email_to,
                    subject,
                    body,
                )

    return _get_appointment(db, appointment.id)


@router.delete(
    "/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST)
    ),
):
    appointment = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id)
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

    old_status = appointment.status.value

    appointment.status = AppointmentStatus.CANCELLED

    _log_audit(
        db=db,
        user_id=current_user.id,
        action="cancel",
        entity_id=appointment.id,
        old_val=old_status,
        new_val=AppointmentStatus.CANCELLED.value,
    )

    db.commit()

    return None