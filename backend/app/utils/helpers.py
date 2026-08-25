import uuid
from datetime import datetime
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from app.core.config import get_settings

settings = get_settings()


def generate_appointment_number() -> str:
    """Generate unique appointment number: APT-YYYYMMDD-XXXX"""
    date_part = datetime.now().strftime("%Y%m%d")
    unique = uuid.uuid4().hex[:6].upper()
    return f"APT-{date_part}-{unique}"


def ensure_upload_dir() -> Path:
    path = Path(settings.UPLOAD_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return path


async def save_upload_file(file: UploadFile, patient_id: int) -> tuple[str, str, str]:
    """Save uploaded file and return (stored_name, original_name, file_type)"""
    ensure_upload_dir()
    ext = Path(file.filename).suffix.lower() if file.filename else ""
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}",
        )

    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {settings.MAX_FILE_SIZE // (1024*1024)} MB",
        )

    stored_name = f"{patient_id}_{uuid.uuid4().hex}{ext}"
    file_path = Path(settings.UPLOAD_DIR) / stored_name
    with open(file_path, "wb") as f:
        f.write(content)

    file_type = ext.lstrip(".")
    original_name = file.filename or stored_name
    return stored_name, original_name, file_type
