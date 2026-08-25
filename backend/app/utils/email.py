from app.core.config import get_settings

settings = get_settings()


def send_email(to: str, subject: str, body: str) -> None:
    """
    Send email. In console mode (default for demo) it just prints.
    Replace with real SMTP (e.g. aiosmtplib) for production.
    """
    if settings.EMAIL_CONSOLE_MODE or not settings.SMTP_HOST:
        print("=" * 60)
        print(f"[EMAIL] To: {to}")
        print(f"[EMAIL] Subject: {subject}")
        print(f"[EMAIL] Body:\n{body}")
        print("=" * 60)
        return

    # Production SMTP placeholder – implement with aiosmtplib / smtplib when needed
    print(f"[EMAIL] Would send to {to}: {subject}")


def appointment_confirmation_email(patient_name: str, doctor_name: str, date: str, time_slot: str, appt_number: str) -> tuple[str, str]:
    subject = f"Appointment Confirmation – {appt_number}"
    body = f"""Dear {patient_name},

Your appointment has been confirmed.

Details:
  Appointment Number : {appt_number}
  Doctor             : {doctor_name}
  Date               : {date}
  Time Slot          : {time_slot}

Please arrive 10 minutes early.

Thank you,
Clinic Management System
"""
    return subject, body


def appointment_reminder_email(patient_name: str, doctor_name: str, date: str, time_slot: str, appt_number: str) -> tuple[str, str]:
    subject = f"Appointment Reminder – {appt_number}"
    body = f"""Dear {patient_name},

This is a friendly reminder for your upcoming appointment.

Details:
  Appointment Number : {appt_number}
  Doctor             : {doctor_name}
  Date               : {date}
  Time Slot          : {time_slot}

Thank you,
Clinic Management System
"""
    return subject, body


def prescription_created_email(patient_name: str, doctor_name: str, diagnosis: str) -> tuple[str, str]:
    subject = "New Prescription Available"
    body = f"""Dear {patient_name},

A new prescription has been created for you by Dr. {doctor_name}.

Diagnosis: {diagnosis}

Please log in to view full details or contact the clinic.

Thank you,
Clinic Management System
"""
    return subject, body
