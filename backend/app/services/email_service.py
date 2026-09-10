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
            "subject": "Reminder: Please Continue on the Platform (4 days)",
            "plainText": f"""
Dear Parent/Caregiver, 

Thank you for signing up for our platform. 

We noticed that there has been no activity on your account for the past four days. Please continue when you have time. 

If you have any questions or trouble accessing the study, please contact the research team: 

Professor Jiesi Guo 
Email: Jiesi.Guo@acu.edu.au 

Dr Kim Rowston 
Email: Kim.Rowston@acu.edu.au 

Dr Chloe Gordon 
Email: Chloe.Gordon@acu.edu.au 
 

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
            "subject": f"Reminder: Reminder to Complete the Baseline Survey (2 Days After Registration) ",
            "plainText": f"""
Dear Parent/Caregiver, 

Thank you for signing up for our platform. 

We noticed that you registered two days ago but have not yet completed the baseline survey. Please complete the survey when you have time. 

Once you complete the survey, you will be able to access the eight study episodes. 

If you have any questions or trouble accessing the study, please contact the research team: 

Professor Jiesi Guo 
Email: Jiesi.Guo@acu.edu.au 

Dr Kim Rowston 
Email: Kim.Rowston@acu.edu.au 

Dr Chloe Gordon 
Email: Chloe.Gordon@acu.edu.au 

Kind regards, 
The Research Team
"""
        }
    }

    poller = client.begin_send(message)
    return poller.result()


def send_post_survey_reminder_email(to_email: str, user_name: str, reminder_number: int):
    client = EmailClient.from_connection_string(settings.AZURE_COMMUNICATION_CONNECTION_STRING)

    message = {
        "senderAddress": settings.AZURE_EMAIL_SENDER,
        "recipients": {
            "to": [{"address": to_email}]
        },
        "content": {
            "subject": "Reminder: Please Complete the Post-Test Survey",
            "plainText": f"""
Dear Parent/Caregiver,

Well done on completing all eight episodes, and thank you for your time and participation.

We noticed that it has been two days since you completed the episodes, but the post-test survey has not yet been completed. Please complete the survey when you have time.

After completing the post-test survey, you will also be eligible to enter the prize draw.

Thank you again for taking part in the study.

If you have any questions or trouble accessing the study, please contact the research team:

Professor Jiesi Guo
Email: Jiesi.Guo@acu.edu.au

Dr Kim Rowston
Email: Kim.Rowston@acu.edu.au

Dr Chloe Gordon
Email: Chloe.Gordon@acu.edu.au

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
