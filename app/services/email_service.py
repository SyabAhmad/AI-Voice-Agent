import smtplib
from email.mime.text import MIMEText
from typing import Optional
from app.core.config import settings
from app.core.logger import logger


async def send_appointment_email(
    to_email: str,
    contact_name: str,
    date: str,
    time: str,
    service_name: str = "Appointment",
) -> bool:
    if not to_email:
        logger.warning("No email address provided. Skipping email.")
        return False

    if not settings.smtp_email or not settings.smtp_password:
        logger.warning("SMTP credentials not configured. Skipping email.")
        return False

    try:
        html_content = f"""
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
        """

        msg = MIMEText(html_content, "html")
        msg["Subject"] = f"Appointment Confirmation - {date} at {time}"
        msg["From"] = settings.smtp_email
        msg["To"] = to_email

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(settings.smtp_email, settings.smtp_password)
        server.send_message(msg)
        server.quit()

        logger.info(f"📧 Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Email sending failed: {e}")
        return False
