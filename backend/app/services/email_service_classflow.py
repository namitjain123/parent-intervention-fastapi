from azure.communication.email import EmailClient

from app.core.config import settings


def send_email(to_email: str, subject: str, html_content: str):
    if not settings.AZURE_COMMUNICATION_CONNECTION_STRING or not settings.AZURE_EMAIL_SENDER:
        print("Azure email not configured")
        return

    client = EmailClient.from_connection_string(settings.AZURE_COMMUNICATION_CONNECTION_STRING)

    message = {
        "senderAddress": settings.AZURE_EMAIL_SENDER,
        "recipients": {
            "to": [{"address": to_email}]
        },
        "content": {
            "subject": subject,
            "html": html_content,
        },
    }

    poller = client.begin_send(message)
    result = poller.result()

    print("Email sent:", result)


def send_class_b_lock_email(to_email: str):
    send_email(
        to_email,
        "Reminder: Platform Episodes Will Open Soon",
        """
        <p>Dear Parent/Caregiver,</p>
        <p>Thank you for completing the baseline survey.</p>
        <p>The episodes are not open yet. They will begin in about 28 days, and we will email you when the first episode is ready.</p>
        <p>Kind regards,</p>
        <p>The Research Team</p>
        """
    )


def send_class_b_unlock_email(to_email: str):
    send_email(
        to_email,
        "Reminder: Platform Episodes Are Now Open (28 days)",
        f"""
        <p>Dear Parent/Caregiver,</p>
        <p>The study episodes are now open.</p>
        <p>Please log in to the study platform and complete the episodes when you have time.</p>
        <p><a href="{settings.FRONTEND_URL}">Open Parenting Platform</a></p>
        <p>If you have any questions or have trouble accessing the platform, please contact the research team.</p>
        <p>Kind regards,</p>
        <p>The Research Team</p>
        """
    )
