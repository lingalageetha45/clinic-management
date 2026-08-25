from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from app.schemas.patient import PatientOut
from app.schemas.doctor import DoctorOut


class PrescriptionCreate(BaseModel):
    appointment_id: Optional[int] = None
    patient_id: int
    doctor_id: int
    diagnosis: str = Field(..., min_length=2)
    medicines: str = Field(..., min_length=2)
    dosage: Optional[str] = None
    instructions: Optional[str] = None
    follow_up_date: Optional[date] = None


class PrescriptionUpdate(BaseModel):
    diagnosis: Optional[str] = None
    medicines: Optional[str] = None
    dosage: Optional[str] = None
    instructions: Optional[str] = None
    follow_up_date: Optional[date] = None


class PrescriptionOut(BaseModel):
    id: int
    appointment_id: Optional[int] = None
    patient_id: int
    doctor_id: int
    diagnosis: str
    medicines: str
    dosage: Optional[str] = None
    instructions: Optional[str] = None
    follow_up_date: Optional[date] = None
    created_at: Optional[datetime] = None
    patient: Optional[PatientOut] = None
    doctor: Optional[DoctorOut] = None

    class Config:
        from_attributes = True
