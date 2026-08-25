from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.core.config import get_settings
from app.core.database import engine, Base
from app.routers import (
    auth,
    doctors,
    patients,
    appointments,
    prescriptions,
    medical_records,
    reports,
)

from app.utils.helpers import ensure_upload_dir


settings = get_settings()


# Create database tables
# For a simple demo; Alembic is preferred in production.
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Appointment Booking & Clinic Management System API",
    docs_url="/docs",
    redoc_url="/redoc",
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Ensure upload directory exists
ensure_upload_dir()


# Mount static files for uploaded medical records
uploads_path = Path(settings.UPLOAD_DIR)

if uploads_path.exists():
    app.mount(
        "/uploads",
        StaticFiles(directory=str(uploads_path)),
        name="uploads",
    )


# API routers
app.include_router(auth.router, prefix="/api")
app.include_router(doctors.router, prefix="/api")
app.include_router(patients.router, prefix="/api")
app.include_router(appointments.router, prefix="/api")
app.include_router(prescriptions.router, prefix="/api")
app.include_router(medical_records.router, prefix="/api")
app.include_router(reports.router, prefix="/api")


@app.get("/", response_class=HTMLResponse)
def root():
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <title>Clinic Management System</title>

        <style>
            * {{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }}

            body {{
                font-family: Arial, Helvetica, sans-serif;
                background: #f5f7fb;
                color: #172033;
                min-height: 100vh;
            }}

            .header {{
                background: #ffffff;
                border-bottom: 1px solid #e5e9f2;
                padding: 20px 7%;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}

            .brand {{
                display: flex;
                align-items: center;
                gap: 12px;
            }}

            .logo {{
                width: 44px;
                height: 44px;
                border-radius: 12px;
                background: #1769aa;
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 22px;
                font-weight: bold;
            }}

            .brand h1 {{
                font-size: 18px;
                margin-bottom: 3px;
            }}

            .brand p {{
                color: #718096;
                font-size: 13px;
            }}

            .status {{
                display: flex;
                align-items: center;
                gap: 8px;
                color: #287d3c;
                font-size: 14px;
                font-weight: 600;
            }}

            .status-dot {{
                width: 9px;
                height: 9px;
                background: #35a854;
                border-radius: 50%;
            }}

            .container {{
                width: 86%;
                max-width: 1200px;
                margin: 0 auto;
            }}

            .hero {{
                text-align: center;
                padding: 75px 20px 45px;
            }}

            .hero h2 {{
                font-size: 38px;
                margin-bottom: 15px;
            }}

            .hero p {{
                max-width: 650px;
                margin: auto;
                color: #667085;
                font-size: 16px;
                line-height: 1.7;
            }}

            .cards {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 24px;
                padding-bottom: 50px;
            }}

            .card {{
                background: white;
                border: 1px solid #e5e9f2;
                border-radius: 16px;
                padding: 30px;
                box-shadow: 0 5px 20px rgba(23, 32, 51, 0.05);
                transition:
                    transform 0.2s ease,
                    box-shadow 0.2s ease;
            }}

            .card:hover {{
                transform: translateY(-4px);
                box-shadow: 0 10px 28px rgba(23, 32, 51, 0.09);
            }}

            .icon {{
                width: 50px;
                height: 50px;
                border-radius: 12px;
                background: #eaf4fb;
                color: #1769aa;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 23px;
                margin-bottom: 22px;
            }}

            .card h3 {{
                font-size: 20px;
                margin-bottom: 10px;
            }}

            .card p {{
                color: #667085;
                font-size: 14px;
                line-height: 1.6;
                min-height: 68px;
            }}

            .button {{
                display: inline-block;
                margin-top: 22px;
                padding: 11px 18px;
                background: #1769aa;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }}

            .button:hover {{
                background: #12588f;
            }}

            .stats {{
                display: flex;
                justify-content: center;
                gap: 70px;
                border-top: 1px solid #e5e9f2;
                padding: 28px 20px;
                margin-bottom: 30px;
            }}

            .stat {{
                text-align: center;
            }}

            .stat strong {{
                display: block;
                font-size: 22px;
                margin-bottom: 5px;
            }}

            .stat span {{
                color: #718096;
                font-size: 13px;
            }}

            .footer {{
                text-align: center;
                color: #8a94a6;
                font-size: 13px;
                padding: 25px;
                border-top: 1px solid #e5e9f2;
                background: white;
            }}

            @media (max-width: 800px) {{
                .cards {{
                    grid-template-columns: 1fr;
                }}

                .header {{
                    padding: 18px 5%;
                }}

                .status {{
                    display: none;
                }}

                .hero h2 {{
                    font-size: 30px;
                }}

                .stats {{
                    gap: 25px;
                    flex-wrap: wrap;
                }}
            }}
        </style>
    </head>

    <body>

        <header class="header">

            <div class="brand">

                <div class="logo">+</div>

                <div>
                    <h1>Clinic Management System</h1>
                    <p>Backend Portal</p>
                </div>

            </div>

            <div class="status">
                <span class="status-dot"></span>
                API Online
            </div>

        </header>


        <main class="container">

            <section class="hero">

                <h2>Welcome to Clinic Management</h2>

                <p>
                    Manage, explore and monitor the clinic management
                    backend services from one central portal.
                </p>

            </section>


            <section class="cards">

                <div class="card">

                    <div class="icon">⌘</div>

                    <h3>API Documentation</h3>

                    <p>
                        Explore and test all available REST API
                        endpoints using the interactive Swagger interface.
                    </p>

                    <a class="button" href="/docs">
                        Open Swagger →
                    </a>

                </div>


                <div class="card">

                    <div class="icon">◇</div>

                    <h3>OpenAPI Specification</h3>

                    <p>
                        View the complete API definition and schema
                        generated by the FastAPI application.
                    </p>

                    <a class="button" href="/openapi.json">
                        View Specification →
                    </a>

                </div>


                <div class="card">

                    <div class="icon">✓</div>

                    <h3>System Health</h3>

                    <p>
                        Check the current availability of the clinic
                        management backend service.
                    </p>

                    <a class="button" href="/health">
                        Check API Health →
                    </a>

                </div>

            </section>


            <section class="stats">

                <div class="stat">
                    <strong>7</strong>
                    <span>API Modules</span>
                </div>

                <div class="stat">
                    <strong>JWT</strong>
                    <span>Authentication</span>
                </div>

                <div class="stat">
                    <strong>PostgreSQL</strong>
                    <span>Database</span>
                </div>

                <div class="stat">
                    <strong>{settings.APP_VERSION}</strong>
                    <span>API Version</span>
                </div>

            </section>

        </main>


        <footer class="footer">
            Clinic Management System
            &nbsp;•&nbsp;
            Appointment Booking &amp; Clinic Management API
        </footer>

    </body>
    </html>
    """


@app.get("/health")
def health():
    return {"status": "ok"}