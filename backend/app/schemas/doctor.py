from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class DoctorCreate(BaseModel):
    full_name: str = Field(..., min_length=2)
    specialization: str
    qualification: str
    phone_number: str
    email: EmailStr
    consultation_fee: float = Field(..., ge=0)
    available_timings: Optional[str] = None


class DoctorUpdate(BaseModel):
    full_name: Optional[str] = None
    specialization: Optional[str] = None
    qualification: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    consultation_fee: Optional[float] = Field(None, ge=0)
    available_timings: Optional[str] = None
    is_active: Optional[bool] = None


class DoctorOut(BaseModel):
    id: int
    full_name: str
    specialization: str
    qualification: str
    phone_number: str
    email: str
    consultation_fee: float
    available_timings: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
