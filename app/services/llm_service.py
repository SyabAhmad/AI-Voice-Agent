from groq import Groq
from app.core.config import settings
from app.core.logger import logger

client = None


def get_groq_client() -> Groq:
    global client
    if client is None:
        client = Groq(api_key=settings.groq_api_key)
    return client


def chat_with_llm(messages: list[dict], model: str = "openai/gpt-oss-120b") -> str:
    try:
        groq = get_groq_client()
        response = groq.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return "Sorry, I'm having trouble processing your request. Please try again."


CLINIC_INFO = {
    "clinic_name": "Our Clinic",
    "services": ["General checkup", "Fever", "Cold", "Flu", "Minor illness"],
    "hours": "Monday-Friday 9AM-5PM, Saturday 10AM-2PM",
    "no_doctor_needed": True,
}

SYSTEM_PROMPT = """STRICT INSTRUCTIONS - FOLLOW EXACTLY:

You are the booking assistant for Our Clinic. 

SAY THIS GREETING FIRST: "Hello! Thank you for calling Our Clinic. How can I help you book an appointment today?"

Current date is 2026-04-16. NEVER suggest dates in the past - always use today or future dates.

THEN ASK FOR (in this exact order):
1. NOT clinic or doctor - we have ONE clinic with any available doctor
2. Full Name? (required)
3. Phone Number? (required)
4. What date? (required - format 2026-04-20 or say "today" or "tomorrow")
5. What time? (required - format 10:00 AM)
6. Email? (optional)

NEVER ASK: "which clinic", "which doctor", "date of birth", "address"

When booking: "Perfect! I'll book your appointment for [date] at [time]. Thank you!"

Be very brief. One question at a time.
"""


def create_initial_message() -> list[dict]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "assistant",
            "content": "Hello! Thank you for calling. How can I help you today?",
        },
    ]


def process_user_message(
    user_message: str, conversation_history: list[dict]
) -> tuple[str, list[dict]]:
    conversation_history.append({"role": "user", "content": user_message})

    response = chat_with_llm(conversation_history)

    conversation_history.append({"role": "assistant", "content": response})

    return response, conversation_history
