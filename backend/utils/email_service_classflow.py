import os
from azure.communication.email import EmailClient
from dotenv import load_dotenv

load_dotenv()

ACS_CONNECTION_STRING = os.getenv("AZURE_COMMUNICATION_CONNECTION_STRING")
ACS_SENDER_EMAIL = os.getenv("AZURE_EMAIL_SENDER")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://gray-sea-01865ef00.7.azurestaticapps.net")


def send_email(to_email: str, subject: str, html_content: str):
    if not ACS_CONNECTION_STRING or not ACS_SENDER_EMAIL:
        print("Azure email not configured")
        return

    client = EmailClient.from_connection_string(ACS_CONNECTION_STRING)

    message = {
        "senderAddress": ACS_SENDER_EMAIL,
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
        "Your next survey will open soon",
        """
        <h2>Your next survey is currently locked</h2>
        <p>Thank you for completing the first questionnaire.</p>
        <p>Your next survey will be available in about 10 minutes.</p>
        <p>Please come back later and continue the program.</p>
        """
    )


def send_class_b_unlock_email(to_email: str):
       
        send_email(
            to_email,
            "Your survey is now available",
            f"""
            <h2>Your next survey is now open</h2>
            <p>You can now return to the Parenting Platform and complete the next survey.</p>
            <p><a href="{FRONTEND_URL}">Open Parenting Platform</a></p>
            """
        )