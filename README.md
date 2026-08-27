# Appointment Booking & Clinic Management System

A backend-focused clinic management platform built with **FastAPI** and **PostgreSQL**. The system provides secure role-based access for administrators, doctors, and receptionists to manage doctors, patients, appointments, prescriptions, and medical records.

---

## 1. Project Overview

The Appointment Booking & Clinic Management System is designed to help clinics manage their daily operations through a RESTful API.

### Main Features

* User registration and login
* JWT-based authentication
* Role-based authorization
* Doctor management
* Patient management
* Appointment scheduling
* Appointment status management
* Prescription management
* Medical record upload and download
* Search and filtering
* Reports dashboard
* Email notifications using FastAPI BackgroundTasks
* PostgreSQL database
* SQLAlchemy ORM
* Alembic database migrations
* Swagger/OpenAPI documentation
* Docker and Docker Compose support

---

## 2. User Roles

The system supports three roles:

### Admin

Admin users can:

* Manage doctors
* Manage patients
* View appointments
* View reports
* Manage system data

### Doctor

Doctors can:

* View assigned appointments
* Update appointment status
* Create prescriptions
* Update prescriptions
* View patient medical history

### Receptionist

Receptionists can:

* Register patients
* Update patient information
* Schedule appointments
* Reschedule appointments
* Cancel appointments

---

## 3. Technology Stack

| Component             | Technology              |
| --------------------- | ----------------------- |
| Backend               | Python                  |
| Framework             | FastAPI                 |
| Database              | PostgreSQL              |
| ORM                   | SQLAlchemy              |
| Authentication        | JWT                     |
| Password Hashing      | bcrypt / Passlib        |
| Migrations            | Alembic                 |
| API Documentation     | Swagger / OpenAPI       |
| Background Processing | FastAPI BackgroundTasks |
| Frontend              | React                   |
| Web Server            | Nginx                   |
| Containerization      | Docker / Docker Compose |

---

## 4. Project Structure

```text
clinic-management/
│
├── backend/
│   ├── app/
│   │   ├── auth/
│   │   │   ├── deps.py
│   │   │   └── security.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   │
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── doctor.py
│   │   │   ├── patient.py
│   │   │   ├── appointment.py
│   │   │   ├── prescription.py
│   │   │   └── medical_record.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── user.py
│   │   │   ├── doctor.py
│   │   │   ├── patient.py
│   │   │   ├── appointment.py
│   │   │   ├── prescription.py
│   │   │   └── medical_record.py
│   │   │
│   │   ├── repositories/
│   │   ├── services/
│   │   ├── routers/
│   │   └── utils/
│   │
│   ├── alembic/
│   ├── uploads/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── seed.py
│
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
│
├── docker-compose.yml
└── README.md
```

---

## 5. Authentication

Authentication is implemented using **JWT access tokens**.

### Register

```http
POST /api/auth/register
```

New registrations are created with the default `receptionist` role.

Example:

```json
{
  "email": "reception@clinic.com",
  "password": "Reception@123",
  "full_name": "Reception Staff"
}
```

### Login

```http
POST /api/auth/login
```

The login endpoint uses OAuth2 password form data.

Example:

```text
username: admin@clinic.com
password: ********
```

### Current User

```http
GET /api/auth/me
```

Requires:

```text
Authorization: Bearer <access_token>
```

---

## 6. Role-Based Authorization

The API uses role-based dependencies to protect endpoints.

Example:

```python
require_roles(UserRole.ADMIN)
```

or:

```python
require_roles(UserRole.ADMIN, UserRole.DOCTOR)
```

Unauthorized users receive an appropriate HTTP `403 Forbidden` response.

---

## 7. Doctor Management

### Create Doctor

```http
POST /api/doctors
```

Admin only.

Example request:

```json
{
  "full_name": "Dr. Priya Sharma",
  "specialization": "General Physician",
  "qualification": "MBBS, MD",
  "phone_number": "9876543210",
  "email": "dr.priya@clinic.com",
  "consultation_fee": 500,
  "available_timings": "Monday to Saturday, 10:00 AM to 2:00 PM"
}
```

### Other Doctor APIs

```http
GET    /api/doctors
GET    /api/doctors/{id}
PUT    /api/doctors/{id}
DELETE /api/doctors/{id}
```

---

## 8. Patient Management

### Create Patient

```http
POST /api/patients
```

Example:

```json
{
  "full_name": "Anita Kumar",
  "age": 32,
  "gender": "Female",
  "phone_number": "9876543211",
  "address": "Bangalore",
  "blood_group": "O+",
  "emergency_contact": "9876543212"
}
```

### Other Patient APIs

```http
GET    /api/patients
GET    /api/patients/{id}
PUT    /api/patients/{id}
DELETE /api/patients/{id}
```

---

## 9. Appointment Management

Appointments contain:

* Appointment number
* Patient
* Doctor
* Appointment date
* Time slot
* Reason for visit
* Status

Supported statuses:

```text
Scheduled
Confirmed
Completed
Cancelled
No Show
```

### APIs

```http
POST   /api/appointments
GET    /api/appointments
GET    /api/appointments/{id}
PUT    /api/appointments/{id}
DELETE /api/appointments/{id}
```

Appointment operations are protected using role-based authorization.

The system also supports appointment filtering and scheduling-related business rules.

---

## 10. Prescription Management

Doctors can create and update prescriptions.

### Create Prescription

```http
POST /api/prescriptions
```

Example:

```json
{
  "appointment_id": 1,
  "patient_id": 1,
  "doctor_id": 1,
  "diagnosis": "Fever",
  "medicines": "Paracetamol 500mg",
  "dosage": "Twice daily",
  "instructions": "Take after food",
  "follow_up_date": "2026-09-05"
}
```

### Other APIs

```http
GET /api/prescriptions
GET /api/prescriptions/{id}
PUT /api/prescriptions/{id}
```

Doctors are restricted to prescriptions associated with their own doctor profile.

A background task is used to notify the patient when a prescription is created.

---

## 11. Medical Records

Medical reports can be uploaded and retrieved for patients.

### Upload

```http
POST /api/medical-records/upload
```

Supported file types:

* PDF
* JPG
* PNG

### List Patient Records

```http
GET /api/medical-records/{patient_id}
```

### Download Record

```http
GET /api/medical-records/download/{record_id}
```

Uploaded files are stored on the server and their metadata is maintained in PostgreSQL.

---

## 12. Reports Dashboard

The reports module provides clinic-level information such as:

* Total patients
* Total doctors
* Today's appointments
* Upcoming appointments
* Completed appointments
* Cancelled appointments
* Most visited doctor
* Average daily appointments

Reports APIs:

```http
GET /api/reports/dashboard
GET /api/reports/appointments
GET /api/reports/doctors
```

---

## 13. Search and Filtering

The system supports filtering and searching of appointment-related information.

Supported criteria include:

* Patient name
* Doctor name
* Appointment number
* Appointment status
* Appointment date
* Doctor specialization

Pagination and query parameters are used where supported by the respective endpoints.

---

## 14. Background Tasks

FastAPI `BackgroundTasks` is used for notification processing without blocking the main API response.

Implemented notification use cases include:

* Appointment confirmation email
* Appointment reminder
* Prescription-created notification

For local development, email can be configured to run in console mode.

---

## 15. Database

The application uses **PostgreSQL** as the primary database.

SQLAlchemy is used as the ORM layer.

Main entities include:

```text
Users
Doctors
Patients
Appointments
Prescriptions
Medical Records
```

Relationships between these entities are maintained using foreign keys and SQLAlchemy relationships.

---

## 16. Database Migrations

Database schema changes are managed using **Alembic**.

Typical commands:

```bash
alembic revision --autogenerate -m "update schema"
alembic upgrade head
```

---

## 17. Running Locally

### Backend

Navigate to the backend directory:

```bash
cd backend
```

Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure the database and application settings in `.env`.

Run the application:

```bash
python -m uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

## 18. Swagger / OpenAPI Documentation

Once the backend is running, Swagger UI is available at:

```text
http://127.0.0.1:8000/docs
```

ReDoc is available at:

```text
http://127.0.0.1:8000/redoc
```

Swagger can be used to:

* View all endpoints
* View request and response schemas
* Authenticate using JWT
* Execute API requests
* Test role-based access

---

## 19. Frontend

The frontend is implemented using React.

The frontend communicates with the FastAPI backend through REST APIs.

The API base URL is configured using:

```text
VITE_API_URL
```

For local development, the default API URL is:

```text
http://localhost:8000/api
```

---

## 20. Docker Setup

Docker support is included for the backend, frontend, and PostgreSQL database.

### Services

The Docker Compose configuration contains:

```text
db        → PostgreSQL
backend   → FastAPI
frontend  → React + Nginx
```

### Start the application

From the project root:

```bash
docker compose up --build
```

The services will be available at:

```text
Frontend: http://localhost:3000
Backend:  http://localhost:8000
Swagger:  http://localhost:8000/docs
```

PostgreSQL runs internally through the Docker Compose network.

The database connection used by the backend is:

```text
postgresql://clinic:clinic123@db:5432/clinic_db
```

For production deployment, the default credentials and secret key should be replaced with secure values.

### Stop the containers

```bash
docker compose down
```

To remove the database volume as well:

```bash
docker compose down -v
```

---

## 21. Docker Files

### Backend

```text
backend/Dockerfile
```

Uses Python 3.11 and runs the FastAPI application with Uvicorn.

### Frontend

```text
frontend/Dockerfile
```

Builds the React application and serves the generated files using Nginx.

### Docker Compose

```text
docker-compose.yml
```

Orchestrates:

* PostgreSQL
* FastAPI backend
* React/Nginx frontend

Persistent Docker volumes are used for:

* PostgreSQL data
* Uploaded medical records

---

## 22. Testing

The API can be tested using:

* Swagger UI
* Postman
* Browser/API clients

Important authentication scenarios to test:

1. Valid login
2. Invalid login
3. Access without JWT
4. Access with JWT
5. Admin-only endpoint with admin
6. Admin-only endpoint with doctor/receptionist
7. Doctor accessing another doctor's prescription
8. Inactive user authentication

---

## 23. API Error Handling

The application uses standard HTTP status codes, including:

```text
200 OK
201 Created
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
422 Validation Error
```

FastAPI validation is used for request validation, while business rules are handled in the application layer.

---

## 24. Security

Security-related features include:

* Password hashing
* JWT authentication
* Protected API endpoints
* Role-based authorization
* Active-user validation
* Input validation
* Restricted access to doctor-specific resources

Sensitive configuration such as database credentials and secret keys should be supplied through environment variables rather than committed to source control.

---

## 25. Deliverables

The project can be submitted with:

* GitHub repository
* Backend source code
* Frontend source code
* README documentation
* Swagger/OpenAPI documentation
* Database schema / ER diagram
* Swagger screenshots
* Postman collection
* Docker setup

---

## 26. Project Status

The core application includes:

* Authentication and authorization
* Doctor management
* Patient management
* Appointment management
* Prescription management
* Medical record management
* Reports
* PostgreSQL integration
* SQLAlchemy ORM
* Alembic migrations
* Background tasks
* Swagger/OpenAPI
* Docker support
* React frontend

Before final submission, verify all required endpoints and role permissions through Swagger/Postman and ensure the Docker setup starts successfully from a clean environment.

---

## 27. Quick Start

### Without Docker

```bash
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

### With Docker

From the project root:

```bash
docker compose up --build
```

Open:

```text
http://localhost:3000
```

Swagger:

```text
http://localhost:8000/docs
```

---

## 28. Conclusion

The Appointment Booking & Clinic Management System provides a structured backend for managing clinic operations with secure authentication, role-based authorization, relational database management, REST APIs, background processing, documentation, and Docker support.
