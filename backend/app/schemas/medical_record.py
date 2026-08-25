from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MedicalRecordOut(BaseModel):
    id: int
    patient_id: int
    uploaded_by: Optional[int] = None
    file_name: str
    original_name: str
    file_type: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
