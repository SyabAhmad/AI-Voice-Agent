from datetime import datetime, timedelta
from typing import Optional

SCHEDULE = {
    "monday": {"start": "09:00", "end": "17:00", "slot_duration": 30},
    "tuesday": {"start": "09:00", "end": "17:00", "slot_duration": 30},
    "wednesday": {"start": "09:00", "end": "17:00", "slot_duration": 30},
    "thursday": {"start": "09:00", "end": "17:00", "slot_duration": 30},
    "friday": {"start": "09:00", "end": "17:00", "slot_duration": 30},
    "saturday": {"start": "10:00", "end": "14:00", "slot_duration": 30},
    "sunday": {"start": "00:00", "end": "00:00", "slot_duration": 0},
}


def get_available_slots(date_str: str) -> list[str]:
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return []

    day_name = date_obj.strftime("%wday").lower().replace("day", "")
    day_map = {
        0: "sunday",
        1: "monday",
        2: "tuesday",
        3: "wednesday",
        4: "thursday",
        5: "friday",
        6: "saturday",
    }
    day_name = day_map.get(date_obj.weekday(), "monday")

    day_schedule = SCHEDULE.get(day_name, SCHEDULE["monday"])

    if day_schedule["slot_duration"] == 0:
        return []

    start_hour, start_min = map(int, day_schedule["start"].split(":"))
    end_hour, end_min = map(int, day_schedule["end"].split(":"))

    slots = []
    current = date_obj.replace(hour=start_hour, minute=start_min)
    end = date_obj.replace(hour=end_hour, minute=end_min)

    while current < end:
        slots.append(current.strftime("%H:%M"))
        current += timedelta(minutes=day_schedule["slot_duration"])

    return slots


def check_availability(date_str: str, time_str: str, booked_slots: list) -> bool:
    slot = f"{date_str} {time_str}"
    return slot not in booked_slots


def format_available_slots(slots: list[str]) -> str:
    if not slots:
        return "No available slots for this date."

    formatted = ", ".join(slots[:5])
    if len(slots) > 5:
        formatted += f", and {len(slots) - 5} more"

    return f"Available times: {formatted}"
