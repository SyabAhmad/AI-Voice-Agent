from typing import Optional
from app.services import crm_service
from app.core.logger import logger


def create_or_update_contact(name: str, phone: str, email: Optional[str] = None):
    return crm_service.get_or_create_contact(phone, name, email)


def book_appointment(
    contact_name: str,
    contact_phone: str,
    contact_email: Optional[str],
    date: str,
    time: str,
    notes: Optional[str] = None,
):
    return crm_service.book_appointment(
        contact_name, contact_phone, contact_email, date, time, notes
    )


def get_appointments_by_date(date: str):
    return crm_service.get_appointments_by_date(date)


def get_available_slots_for_date(date: str):
    return crm_service.get_available_slots(date)
