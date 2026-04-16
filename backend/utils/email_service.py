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
            "subject": "Reminder to continue your Parent Intervention program",
            "plainText": f"""
Hi {user_name},

This is a friendly reminder to continue your Parent Intervention program.

We noticed that you have not completed the next required step yet. Please log in and continue when convenient.

Thank you.
"""
        }
    }

    poller = client.begin_send(message)
    return poller.result()