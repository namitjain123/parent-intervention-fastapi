import os
from azure.communication.email import EmailClient

def send_reminder_email(to_email: str, user_name: str):
    connection_string = os.getenv("AZURE_COMMUNICATION_CONNECTION_STRING")
    sender_address = os.getenv("AZURE_EMAIL_SENDER")

    client = EmailClient.from_connection_string(connection_string)

    message = {
        "senderAddress": sender_address,
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

def send_25day_progress_reminder(to_email: str, user_name: str):
    connection_string = os.getenv("AZURE_COMMUNICATION_CONNECTION_STRING")
    sender_address = os.getenv("AZURE_EMAIL_SENDER")

    client = EmailClient.from_connection_string(connection_string)

    message = {
        "senderAddress": sender_address,
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