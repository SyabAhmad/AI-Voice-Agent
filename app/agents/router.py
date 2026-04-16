from typing import Optional
from enum import Enum


class IntentType(str, Enum):
    BOOK_APPOINTMENT = "book_appointment"
    CHECK_AVAILABILITY = "check_availability"
    CANCEL_APPOINTMENT = "cancel_appointment"
    RESCHEDULE = "reschedule"
    GENERAL_INQUIRY = "general_inquiry"
    UNKNOWN = "unknown"


def detect_intent(user_message: str) -> IntentType:
    message_lower = user_message.lower()

    booking_keywords = [
        "book",
        "appointment",
        "schedule",
        "reserve",
        "meeting",
        "schedule time",
    ]
    if any(keyword in message_lower for keyword in booking_keywords):
        return IntentType.BOOK_APPOINTMENT

    availability_keywords = ["available", "free", "slots", "when can", "open"]
    if any(keyword in message_lower for keyword in availability_keywords):
        return IntentType.CHECK_AVAILABILITY

    cancel_keywords = ["cancel", "don't want", "not coming", "cancel appointment"]
    if any(keyword in message_lower for keyword in cancel_keywords):
        return IntentType.CANCEL_APPOINTMENT

    reschedule_keywords = ["reschedule", "change time", "change date", "different time"]
    if any(keyword in message_lower for keyword in reschedule_keywords):
        return IntentType.RESCHEDULE

    return IntentType.GENERAL_INQUIRY


def route_intent(intent: IntentType, user_message: str, context: dict) -> dict:
    if intent == IntentType.BOOK_APPOINTMENT:
        return {
            "action": "collect_booking_details",
            "prompt": "I'd be happy to help you book an appointment. Could you please tell me your name?",
        }

    elif intent == IntentType.CHECK_AVAILABILITY:
        return {
            "action": "check_availability",
            "prompt": "Sure! Which date would you like to check availability for? (YYYY-MM-DD format)",
        }

    elif intent == IntentType.CANCEL_APPOINTMENT:
        return {
            "action": "cancel_appointment",
            "prompt": "I'm sorry to hear that. Could you please provide your appointment details?",
        }

    elif intent == IntentType.RESCHEDULE:
        return {
            "action": "reschedule_appointment",
            "prompt": "No problem. What new date and time would work for you?",
        }

    else:
        return {
            "action": "general_response",
            "prompt": "I can help you with booking appointments, checking availability, or managing existing bookings. How can I assist you?",
        }


def parse_booking_details(user_message: str) -> Optional[dict]:
    return None
