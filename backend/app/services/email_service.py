from azure.communication.email import EmailClient

from app.core.config import settings


def make_email_client() -> EmailClient:
    """
    EmailClient that fails fast instead of blocking.

    The SDK defaults are 10 retries and 300s connect/read timeouts, all inside
    begin_send() - long before the poller.result() timeout below is reached.
    Worse, when Azure throttles it replies with Retry-After and the SDK sleeps
    for exactly that long with no upper bound, even with a single retry. With
    many users queued, one throttled job sat asleep for minutes and every later
    tick was skipped ("maximum number of running instances reached").

    retry_total=0 means a throttled or failed send raises immediately. That's
    safe because the scheduler already re-runs every job each interval - it is
    the retry mechanism - so SDK-level retries only ever added blocking.
    """
    return EmailClient.from_connection_string(
        settings.AZURE_COMMUNICATION_CONNECTION_STRING,
        retry_total=0,
        connection_timeout=10,
        read_timeout=20,
    )


def send_reminder_email(to_email: str, user_name: str):
    client = make_email_client()

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
    # poller.result(timeout=N) does not raise on timeout - it just stops
    # waiting and returns whatever is available. Without checking done()
    # explicitly, a hung Azure Communication Services call would block the
    # scheduler job that called this indefinitely, with nothing ever
    # raising to trigger the caller's own except-and-continue handling.
    result = poller.result(timeout=30)

    if not poller.done():
        raise TimeoutError(f"Email send to {to_email} did not complete within 30s")

    return result


def send_pre_survey_reminder_email(to_email: str, user_name: str, reminder_number: int):
    client = make_email_client()

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
    # poller.result(timeout=N) does not raise on timeout - it just stops
    # waiting and returns whatever is available. Without checking done()
    # explicitly, a hung Azure Communication Services call would block the
    # scheduler job that called this indefinitely, with nothing ever
    # raising to trigger the caller's own except-and-continue handling.
    result = poller.result(timeout=30)

    if not poller.done():
        raise TimeoutError(f"Email send to {to_email} did not complete within 30s")

    return result


def send_post_survey_reminder_email(to_email: str, user_name: str, reminder_number: int):
    client = make_email_client()

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
    # poller.result(timeout=N) does not raise on timeout - it just stops
    # waiting and returns whatever is available. Without checking done()
    # explicitly, a hung Azure Communication Services call would block the
    # scheduler job that called this indefinitely, with nothing ever
    # raising to trigger the caller's own except-and-continue handling.
    result = poller.result(timeout=30)

    if not poller.done():
        raise TimeoutError(f"Email send to {to_email} did not complete within 30s")

    return result


def send_25day_progress_reminder(to_email: str, user_name: str):
    client = make_email_client()

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
    # poller.result(timeout=N) does not raise on timeout - it just stops
    # waiting and returns whatever is available. Without checking done()
    # explicitly, a hung Azure Communication Services call would block the
    # scheduler job that called this indefinitely, with nothing ever
    # raising to trigger the caller's own except-and-continue handling.
    result = poller.result(timeout=30)

    if not poller.done():
        raise TimeoutError(f"Email send to {to_email} did not complete within 30s")

    return result
