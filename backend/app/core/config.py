from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Clinic Appointment Booking System"
    APP_VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str = (
        "postgresql://clinic:clinic123@127.0.0.1:5432/clinic_db"
    )

    # Authentication
    SECRET_KEY: str = "dev-secret-key-change-in-production"

    # Email
    EMAIL_CONSOLE_MODE: bool = True

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # File uploads
    UPLOAD_DIR: str = "uploads"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()