from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.appointment import AppointmentStatus
from app.schemas.patient import PatientOut
from app.schemas.doctor import DoctorOut


class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    time_slot: str
    reason_for_visit: Optional[str] = None


class AppointmentUpdate(BaseModel):
    appointment_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    time_slot: Optional[str] = None
    reason_for_visit: Optional[str] = None
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = None


class AppointmentOut(BaseModel):
    id: int
    appointment_number: str
    patient_id: int
    doctor_id: int
    appointment_date: str
    time_slot: str
    reason_for_visit: Optional[str] = None
    status: AppointmentStatus
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    patient: Optional[PatientOut] = None
    doctor: Optional[DoctorOut] = None

    class Config:
        from_attributes = True
