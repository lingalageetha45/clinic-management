from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class PatientCreate(BaseModel):
    full_name: str = Field(..., min_length=2)
    age: int = Field(..., ge=0, le=150)
    gender: str
    phone_number: str
    address: Optional[str] = None
    blood_group: Optional[str] = None
    emergency_contact: Optional[str] = None
    email: Optional[EmailStr] = None


class PatientUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = Field(None, ge=0, le=150)
    gender: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    blood_group: Optional[str] = None
    emergency_contact: Optional[str] = None
    email: Optional[EmailStr] = None


class PatientOut(BaseModel):
    id: int
    full_name: str
    age: int
    gender: str
    phone_number: str
    address: Optional[str] = None
    blood_group: Optional[str] = None
    emergency_contact: Optional[str] = None
    email: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
