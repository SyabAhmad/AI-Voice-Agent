from typing import Optional
import httpx
from app.core.config import settings
from app.core.logger import logger


async def send_appointment_email(
    to_email: str,
    contact_name: str,
    date: str,
    time: str,
    service_name: str = "Appointment",
) -> bool:
    if (
        not settings.brevo_api_key
        or settings.brevo_api_key == "xsh-xxxxxxxxxxxxxxxxxxxxxxxx"
    ):
        logger.warning("Brevo API key not configured. Skipping email.")
        return False

    url = "https://api.brevo.com/v3/smtp/email"

    payload = {
        "sender": {"name": "Appointment Booking", "email": "noreply@yourdomain.com"},
        "to": [{"email": to_email, "name": contact_name}],
        "subject": f"Appointment Confirmation - {date} at {time}",
        "htmlContent": f"""
        <html>
        <body>
            <h2>Appointment Confirmed!</h2>
            <p>Hello {contact_name},</p>
            <p>Your appointment has been successfully booked.</p>
            <p><strong>Date:</strong> {date}</p>
            <p><strong>Time:</strong> {time}</p>
            <p><strong>Service:</strong> {service_name}</p>
            <p>We look forward to seeing you!</p>
            <p>Best regards,<br>Appointment Booking Team</p>
        </body>
        </html>
        """,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                headers={
                    "api-key": settings.brevo_api_key,
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )

            if response.status_code in [200, 201]:
                logger.info(f"Email sent successfully to {to_email}")
                return True
            else:
                logger.error(
                    f"Brevo API error: {response.status_code} - {response.text}"
                )
                return False
    except Exception as e:
        logger.error(f"Email sending failed: {e}")
        return False
