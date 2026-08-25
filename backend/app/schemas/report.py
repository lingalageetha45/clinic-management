from pydantic import BaseModel
from typing import Optional, List


class DashboardStats(BaseModel):
    total_patients: int
    total_doctors: int
    todays_appointments: int
    upcoming_appointments: int
    completed_appointments: int
    cancelled_appointments: int
    most_visited_doctor: Optional[str] = None
    average_daily_appointments: float
