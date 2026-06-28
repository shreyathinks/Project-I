"""
Email notification utilities using aiosmtplib for async SMTP sending.
Falls back to a no-op log when SMTP credentials are not configured.
"""

import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

from config.settings import settings

logger = logging.getLogger(__name__)


async def send_email(
    to_addresses: List[str],
    subject: str,
    body_html: str,
    body_text: str = "",
) -> bool:
    """Send an email asynchronously. Returns True on success."""
    if not settings.notifications_enabled or not settings.smtp_user:
        logger.info("Email notifications disabled or SMTP not configured. Skipping send.")
        return False

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.email_from or settings.smtp_user
        msg["To"] = ", ".join(to_addresses)

        if body_text:
            msg.attach(MIMEText(body_text, "plain"))
        msg.attach(MIMEText(body_html, "html"))

        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_password,
            start_tls=True,
        )
        logger.info("Email sent to %s: %s", to_addresses, subject)
        return True

    except Exception as exc:
        logger.error("Failed to send email: %s", exc)
        return False


async def send_expiry_warning(user_email: str, items: list) -> bool:
    subject = "🥦 Kitchen Alert: Items Expiring Soon"
    item_rows = "".join(
        f"<tr><td>{i['name']}</td><td>{i['days_until_expiry']} days</td></tr>"
        for i in items
    )
    body_html = f"""
    <h2>Items Expiring Soon</h2>
    <table border="1" cellpadding="6">
      <tr><th>Item</th><th>Expires In</th></tr>
      {item_rows}
    </table>
    <p>Log in to your Kitchen Platform to take action.</p>
    """
    return await send_email([user_email], subject, body_html)
