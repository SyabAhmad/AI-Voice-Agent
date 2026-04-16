from fastapi import APIRouter, Request
import json
from datetime import datetime, timedelta
from typing import Optional
from app.core.logger import logger
from app.services import booking_service
from app.services import email_service

router = APIRouter()


def extract_args(body: dict) -> dict:
    """
    Extract arguments from Retell request body.
    Primary sources:
    - body["args"] (dict or JSON string)
    - body["call"]["collected_dynamic_variables"] (Retell dynamic variables)
    - body["call"]["arguments"] (legacy)
    """
    args = {}

    # Primary: body["args"] - Retell's standard format
    raw_args = body.get("args")

    if raw_args is not None:
        if isinstance(raw_args, str):
            try:
                args = json.loads(raw_args)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse args string: {raw_args[:100]}")
                args = {}
        elif isinstance(raw_args, dict):
            args = raw_args
        else:
            logger.warning(f"Unexpected args type: {type(raw_args)}")

    # Check collected_dynamic_variables (Retell dynamic variables)
    if not args:
        call_data = body.get("call", {})
        collected_vars = call_data.get("collected_dynamic_variables", {})
        if collected_vars:
            logger.info(f"📡 Using collected_dynamic_variables: {collected_vars}")
            # Map common field names
            args = {
                "name": collected_vars.get("name", ""),
                "phone": collected_vars.get("phone", ""),
                "email": collected_vars.get("email", ""),
                "requested_date": collected_vars.get("requested_date", ""),
                "requested_time": collected_vars.get("requested_time", ""),
            }

    # Fallback: body["call"]["arguments"] (legacy nested format)
    if not args:
        call_data = body.get("call", {})
        raw_args = call_data.get("arguments")
        if raw_args is not None:
            if isinstance(raw_args, str):
                try:
                    args = json.loads(raw_args)
                except json.JSONDecodeError:
                    logger.warning(
                        f"Failed to parse call.arguments string: {raw_args[:100]}"
                    )
            elif isinstance(raw_args, dict):
                args = raw_args

    # Fallback: flat JSON body
    if not args:
        known_fields = {"name", "phone", "email", "requested_date", "requested_time"}
        direct_fields = {k: v for k, v in body.items() if k in known_fields and v}
        if direct_fields:
            args = direct_fields

    return {
        "name": args.get("name", ""),
        "phone": args.get("phone", ""),
        "email": args.get("email", ""),
        "requested_date": args.get("requested_date", ""),
        "requested_time": args.get("requested_time", ""),
    }


def normalize_date(date_str: str) -> Optional[str]:
    """Convert relative dates ('tomorrow', 'today', 'next week') to YYYY-MM-DD."""
    if not date_str:
        return None

    date_str = date_str.lower().strip()

    if date_str in ("tomorrow", "today", "next week"):
        days_map = {
            "today": 0,
            "tomorrow": 1,
            "next week": 7,
        }
        days = days_map.get(date_str, 0)
        return (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        if date_obj.date() < datetime.now().date():
            return None
        return date_str
    except ValueError:
        return None


def clean_appointment_data(raw: dict) -> dict:
    """
    Normalize and validate extracted data.
    Returns cleaned dict with normalized date.
    """
    name = raw.get("name", "").strip() if raw.get("name") else ""
    phone = raw.get("phone", "").strip() if raw.get("phone") else ""
    email = raw.get("email", "").strip() if raw.get("email") else ""
    requested_date = (
        raw.get("requested_date", "").strip() if raw.get("requested_date") else ""
    )
    requested_time = (
        raw.get("requested_time", "").strip() if raw.get("requested_time") else ""
    )

    # Normalize date (e.g., "tomorrow" -> "2026-04-17")
    if requested_date:
        normalized = normalize_date(requested_date)
        if normalized:
            requested_date = normalized
        else:
            requested_date = ""

    return {
        "name": name,
        "phone": phone,
        "email": email,
        "requested_date": requested_date,
        "requested_time": requested_time,
    }


def validate_appointment_data(data: dict) -> tuple[bool, list[str]]:
    """Validate required fields. Returns (is_valid, missing_fields)."""
    required = ["name", "phone", "requested_date", "requested_time"]
    missing = [field for field in required if not data.get(field)]
    return len(missing) == 0, missing


@router.post("/book-appointment")
async def book_appointment(request: Request):
    """Book appointment endpoint."""
    try:
        body = await request.json()
        logger.info(f"📥 Incoming request: {json.dumps(body)[:300]}")

        # Step 1: Extract raw args
        raw_args = extract_args(body)

        # Step 2: Clean and normalize
        data = clean_appointment_data(raw_args)

        logger.info(
            f"📝 Processed: name={data['name']}, phone={data['phone']}, "
            f"date={data['requested_date']}, time={data['requested_time']}"
        )

        # Step 3: Validate
        is_valid, missing = validate_appointment_data(data)
        if not is_valid:
            return {
                "success": False,
                "error": f"Missing required fields: {', '.join(missing)}",
            }

        # Step 4: Book appointment
        try:
            contact = booking_service.create_or_update_contact(
                data["name"], data["phone"], data["email"]
            )
            appointment = booking_service.book_appointment(
                data["name"],
                data["phone"],
                data["email"],
                data["requested_date"],
                data["requested_time"],
            )
        except ValueError as e:
            logger.warning(f"Booking conflict: {e}")
            return {
                "success": False,
                "error": str(e),
            }

        logger.info(
            f"✅ Booked: {data['name']} on {data['requested_date']} at {data['requested_time']}"
        )

        if data.get("email"):
            email_sent = await email_service.send_appointment_email(
                to_email=data["email"],
                contact_name=data["name"],
                date=data["requested_date"],
                time=data["requested_time"],
            )
            if email_sent:
                logger.info(f"📧 Confirmation email sent to {data['email']}")
            else:
                logger.warning(f"📧 Failed to send email to {data['email']}")

        return {
            "success": True,
            "message": "Appointment booked successfully",
            "data": {
                "name": data["name"],
                "phone": data["phone"],
                "email": data["email"],
                "requested_date": data["requested_date"],
                "requested_time": data["requested_time"],
            },
        }

    except Exception as e:
        logger.error(f"Error in /book-appointment: {e}")
        return {"success": False, "error": str(e)}


@router.post("/check-availability")
async def check_availability(request: Request):
    """Check available slots endpoint."""
    try:
        body = await request.json()
        logger.info(f"📥 Check availability request: {json.dumps(body)[:500]}")

        # Extract and clean
        raw_args = extract_args(body)
        logger.info(f"📝 Raw args extracted: {raw_args}")

        data = clean_appointment_data(raw_args)
        logger.info(f"📝 Cleaned data: {data}")

        requested_date = data.get("requested_date")

        if not requested_date:
            logger.warning("⚠️ No requested_date in check-availability")
            return {"available": False, "requested_date": "", "available_slots": []}

        try:
            slots = booking_service.get_available_slots_for_date(requested_date)
            logger.info(f"📅 Slots for {requested_date}: {slots}")
        except Exception as e:
            logger.warning(f"Error getting slots, using defaults: {e}")
            slots = ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"]

        response = {
            "available": len(slots) > 0,
            "requested_date": requested_date,
            "available_slots": slots[:10],
        }
        logger.info(f"📤 Sending response: {response}")
        return response

    except Exception as e:
        logger.error(f"Error in /check-availability: {e}")
        return {"available": False, "requested_date": "", "available_slots": []}


@router.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
