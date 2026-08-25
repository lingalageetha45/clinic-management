from sqlalchemy import (
    Column, Integer, String, DateTime, Text, ForeignKey, Enum as SAEnum, UniqueConstraint
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = (
        UniqueConstraint("doctor_id", "appointment_date", "time_slot", name="uq_doctor_slot"),
    )

    id = Column(Integer, primary_key=True, index=True)
    appointment_number = Column(String(50), unique=True, index=True, nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    appointment_date = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    time_slot = Column(String(20), nullable=False)  # e.g. "10:00-10:30"
    reason_for_visit = Column(Text, nullable=True)
    status = Column(SAEnum(AppointmentStatus), default=AppointmentStatus.SCHEDULED, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    patient = relationship("Patient", backref="appointments")
    doctor = relationship("Doctor", backref="appointments")
