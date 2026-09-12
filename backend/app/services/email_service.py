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
            "subject": "Reminder: Please Continue on the Platform",
            "html": """
        <p>Dear Parent/Caregiver,</p>
        <p>Thank you for signing up for our platform.</p>
        <p>We noticed that there has been no activity on your account for the past four days. Please continue when you have time.</p>
        <p>If you have any questions or trouble accessing the study, please contact the research team:</p>
        <p>Professor Jiesi Guo<br>Email: <a href="mailto:Jiesi.Guo@acu.edu.au">Jiesi.Guo@acu.edu.au</a></p>
        <p>Dr Kim Rowston<br>Email: <a href="mailto:Kim.Rowston@acu.edu.au">Kim.Rowston@acu.edu.au</a></p>
        <p>Dr Chloe Gordon<br>Email: <a href="mailto:Chloe.Gordon@acu.edu.au">Chloe.Gordon@acu.edu.au</a></p>
        <p>Kind regards,</p>
        <p>The Research Team</p>
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
            "subject": f"Reminder: Reminder to Complete the Baseline Survey",
            "html": """
        <p>Dear Parent/Caregiver,</p>
        <p>Thank you for signing up for our platform.</p>
        <p>We noticed that you registered two days ago but have not yet completed the baseline survey. Please complete the survey when you have time.</p>
        <p>Once you complete the survey, you will be able to access the eight study episodes.</p>
        <p>If you have any questions or trouble accessing the study, please contact the research team:</p>
        <p>Professor Jiesi Guo<br>Email: <a href="mailto:Jiesi.Guo@acu.edu.au">Jiesi.Guo@acu.edu.au</a></p>
        <p>Dr Kim Rowston<br>Email: <a href="mailto:Kim.Rowston@acu.edu.au">Kim.Rowston@acu.edu.au</a></p>
        <p>Dr Chloe Gordon<br>Email: <a href="mailto:Chloe.Gordon@acu.edu.au">Chloe.Gordon@acu.edu.au</a></p>
        <p>Kind regards,</p>
        <p>The Research Team</p>
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
            "html": """
        <p>Dear Parent/Caregiver,</p>
        <p>Well done on completing all eight episodes, and thank you for your time and participation.</p>
        <p>We noticed that it has been two days since you completed the episodes, but the post-test survey has not yet been completed. Please complete the survey when you have time.</p>
        <p>After completing the post-test survey, you will also be eligible to enter the prize draw.</p>
        <p>Thank you again for taking part in the study.</p>
        <p>If you have any questions or trouble accessing the study, please contact the research team:</p>
        <p>Professor Jiesi Guo<br>Email: <a href="mailto:Jiesi.Guo@acu.edu.au">Jiesi.Guo@acu.edu.au</a></p>
        <p>Dr Kim Rowston<br>Email: <a href="mailto:Kim.Rowston@acu.edu.au">Kim.Rowston@acu.edu.au</a></p>
        <p>Dr Chloe Gordon<br>Email: <a href="mailto:Chloe.Gordon@acu.edu.au">Chloe.Gordon@acu.edu.au</a></p>
        <p>Kind regards,</p>
        <p>The Research Team</p>
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


