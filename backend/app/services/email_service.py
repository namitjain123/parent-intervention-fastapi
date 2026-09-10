from azure.communication.email import EmailClient

from app.core.config import settings


def send_reminder_email(to_email: str, user_name: str):
    client = EmailClient.from_connection_string(settings.AZURE_COMMUNICATION_CONNECTION_STRING)

    message = {
        "senderAddress": settings.AZURE_EMAIL_SENDER,
        "recipients": {
            "to": [{"address": to_email}]
        },
        "content": {
            "subject": "Reminder: Please Continue on the Platform (7 days)",
            "plainText": f"""
Dear Parent/Caregiver,

Thank you for signing up for our platform.

We noticed that there has been no activity on your account for the past seven days. Please continue when you have time.

If you have any questions or trouble accessing the study, please contact the research team.

Kind regards,

The Research Team
"""
        }
    }

    poller = client.begin_send(message)
    return poller.result()


def send_pre_survey_reminder_email(to_email: str, user_name: str, reminder_number: int):
    client = EmailClient.from_connection_string(settings.AZURE_COMMUNICATION_CONNECTION_STRING)

    message = {
        "senderAddress": settings.AZURE_EMAIL_SENDER,
        "recipients": {
            "to": [{"address": to_email}]
        },
        "content": {
            "subject": f"Reminder: Please Complete Your Pre-Questionnaire ({reminder_number}/{settings.PRE_SURVEY_REMINDER_MAX_COUNT})",
            "plainText": f"""
Dear Parent/Caregiver,

Thank you for signing up for our platform.

We noticed that you haven't started the pre-questionnaire yet. This step is required before you can access any episodes. Please log in and complete it when you have a moment: {settings.FRONTEND_URL}

If you have any questions or trouble accessing the study, please contact the research team.

Kind regards,

The Research Team
"""
        }
    }

    poller = client.begin_send(message)
    return poller.result()


def send_25day_progress_reminder(to_email: str, user_name: str):
    client = EmailClient.from_connection_string(settings.AZURE_COMMUNICATION_CONNECTION_STRING)

    message = {
        "senderAddress": settings.AZURE_EMAIL_SENDER,
        "recipients": {
            "to": [{"address": to_email}]
        },
        "content": {
            "subject": "Reminder: Platform Will Close in One Week (21 days)",
            "plainText": f"""
Dear Parent/Caregiver,

We noticed that the episodes have not yet been completed. Please complete them as soon as possible. The study platform will automatically close in one week, after which you will no longer be able to access the episodes.

If you have any questions or have trouble accessing the platform, please contact the research team.

Kind regards,

The Research Team
"""
        }
    }

    poller = client.begin_send(message)
    return poller.result()
