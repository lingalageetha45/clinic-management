from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from pathlib import Path

from app.core.database import get_db
from app.core.config import get_settings
from app.models.medical_record import MedicalRecord
from app.models.patient import Patient
from app.models.user import User, UserRole
from app.schemas.medical_record import MedicalRecordOut
from app.auth.deps import get_current_user, require_roles
from app.utils.helpers import save_upload_file

router = APIRouter(prefix="/medical-records", tags=["Medical Records"])
settings = get_settings()


@router.post("/upload", response_model=MedicalRecordOut, status_code=status.HTTP_201_CREATED)
async def upload_medical_record(
    patient_id: int = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.DOCTOR, UserRole.RECEPTIONIST)),
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    stored_name, original_name, file_type = await save_upload_file(file, patient_id)
    record = MedicalRecord(
        patient_id=patient_id,
        uploaded_by=current_user.id,
        file_name=stored_name,
        original_name=original_name,
        file_type=file_type,
        file_path=str(Path(settings.UPLOAD_DIR) / stored_name),
        description=description,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


# Static path first so it is not captured by /{patient_id}
@router.get("/download/{record_id}")
def download_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    path = Path(record.file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found on server")
    return FileResponse(
        path=path,
        filename=record.original_name,
        media_type="application/octet-stream",
    )


@router.get("/{patient_id}", response_model=List[MedicalRecordOut])
def list_patient_records(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    records = (
        db.query(MedicalRecord)
        .filter(MedicalRecord.patient_id == patient_id)
        .order_by(MedicalRecord.created_at.desc())
        .all()
    )
    return records
