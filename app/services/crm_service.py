import gspread
from google.oauth2 import service_account
from typing import Optional
from datetime import datetime
from app.core.logger import logger

CREDENTIALS_FILE = "app/credentials.json"
SPREADSHEET_NAME = "aivoice"

gc = None
sheet = None


def get_google_sheet():
    global gc, sheet
    if sheet is None:
        try:
            gc = gspread.service_account(filename=CREDENTIALS_FILE)
            sheet = gc.open(SPREADSHEET_NAME)
            logger.info(f"Connected to Google Sheets: {SPREADSHEET_NAME}")

            # Ensure worksheets exist
            try:
                sheet.worksheet("Contacts")
            except:
                sheet.add_worksheet("Contacts", rows=100, cols=5)
                ws = sheet.worksheet("Contacts")
                ws.append_row(["id", "name", "phone", "email", "created_at"])
                logger.info("Created Contacts worksheet")

            try:
                sheet.worksheet("Appointments")
            except:
                sheet.add_worksheet("Appointments", rows=100, cols=10)
                ws = sheet.worksheet("Appointments")
                ws.append_row(
                    [
                        "id",
                        "name",
                        "phone",
                        "email",
                        "date",
                        "time",
                        "status",
                        "notes",
                        "booked_at",
                    ]
                )
                logger.info("Created Appointments worksheet")

        except Exception as e:
            logger.error(f"Failed to connect to Google Sheets: {e}")
            raise
    return sheet


def get_or_create_contact(phone: str, name: str, email: Optional[str] = None) -> dict:
    try:
        sheet = get_google_sheet()
        contacts_ws = sheet.worksheet("Contacts")

        # Get all records - skip header
        all_contacts = contacts_ws.get_all_records()

        logger.info(f"Total contacts in sheet: {len(all_contacts)}")

        for idx, contact in enumerate(all_contacts, start=2):
            if str(contact.get("phone", "")).replace("+", "") == phone.replace("+", ""):
                contacts_ws.update_cell(idx, 2, name)
                if email:
                    contacts_ws.update_cell(idx, 4, email)
                logger.info(f"Updated contact: {name}")
                return contact

        row_num = len(all_contacts) + 2
        row = [row_num - 1, name, phone, email or "", datetime.now().isoformat()]
        contacts_ws.append_row(row)

        logger.info(f"New contact added: {name} ({phone})")
        return {"name": name, "phone": phone, "email": email}
    except Exception as e:
        logger.error(f"Contact Error: {e}")
        return {"name": name, "phone": phone, "email": email}


def book_appointment(
    contact_name: str,
    contact_phone: str,
    contact_email: Optional[str],
    date: str,
    time: str,
    notes: Optional[str] = None,
) -> dict:
    try:
        sheet = get_google_sheet()
        appointments_ws = sheet.worksheet("Appointments")

        all_appointments = appointments_ws.get_all_records()

        logger.info(f"Total appointments in sheet: {len(all_appointments)}")

        row_num = len(all_appointments) + 2
        row = [
            row_num - 1,
            contact_name,
            contact_phone,
            contact_email or "",
            date,
            time,
            "confirmed",
            notes or "",
            datetime.now().isoformat(),
        ]
        appointments_ws.append_row(row)

        logger.info(f"Appointment booked: {contact_name} on {date} at {time}")
        return {
            "contact_name": contact_name,
            "date": date,
            "time": time,
            "status": "confirmed",
        }
    except Exception as e:
        logger.error(f"Booking Error: {e}")
        raise


def get_appointments_by_date(date: str) -> list[dict]:
    sheet = get_google_sheet()
    appointments_ws = sheet.worksheet("Appointments")
    all_appointments = appointments_ws.get_all_records()
    return [
        apt
        for apt in all_appointments
        if apt.get("date") == date and apt.get("status") == "confirmed"
    ]


def get_available_slots(date: str) -> list[str]:
    from app.data.schedule import get_available_slots as get_schedule_slots

    schedule_slots = get_schedule_slots(date)
    booked = get_appointments_by_date(date)
    booked_times = [apt.get("time") for apt in booked]
    available = [slot for slot in schedule_slots if slot not in booked_times]
    return available
