from app.core.config import settings
from app.services.email_service import make_email_client


def send_email(to_email: str, subject: str, html_content: str):
    if not settings.AZURE_COMMUNICATION_CONNECTION_STRING or not settings.AZURE_EMAIL_SENDER:
        print("Azure email not configured")
        return

    client = make_email_client()

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
    # poller.result(timeout=N) does not raise on timeout - it just stops
    # waiting and returns whatever is available, even if the send never
    # completed. Without checking done() explicitly, a hung Azure
    # Communication Services call would block this call indefinitely
    # (this function used to run inline inside an HTTP request), and the
    # caller's try/except would never fire since nothing ever raised.
    result = poller.result(timeout=30)

    if not poller.done():
        raise TimeoutError(f"Email send to {to_email} did not complete within 30s")

    print("Email sent:", result)


def send_class_b_lock_email(to_email: str):
    send_email(
        to_email,
        "Reminder: Platform Episodes Will Open Soon",
        """
        <p>Dear Parent/Caregiver,</p>
        <p>Thank you for completing the baseline survey.</p>
        <p>The episodes are not open yet. They will begin in about 28 days, and we will email you when the first episode is ready.</p>
        <p>If you have any questions or trouble accessing the study, please contact the research team:</p>
        <p>Professor Jiesi Guo<br>Email: Jiesi.Guo@acu.edu.au</p>
        <p>Dr Kim Rowston<br>Email: Kim.Rowston@acu.edu.au</p>
        <p>Dr Chloe Gordon<br>Email: Chloe.Gordon@acu.edu.au</p>
        <p>Kind regards,</p>
        <p>The Research Team</p>
        """
    )


def send_class_b_unlock_email(to_email: str):
    send_email(
        to_email,
        "Reminder: Platform Episodes Are Now Open",
        """
        <p>Dear Parent/Caregiver,</p>
        <p>The study episodes are now open.</p>
        <p>Please log in to the study platform and complete the episodes when you have time.</p>
        <p>If you have any questions or trouble accessing the study, please contact the research team:</p>
        <p>Professor Jiesi Guo<br>Email: Jiesi.Guo@acu.edu.au</p>
        <p>Dr Kim Rowston<br>Email: Kim.Rowston@acu.edu.au</p>
        <p>Dr Chloe Gordon<br>Email: Chloe.Gordon@acu.edu.au</p>
        <p>Kind regards,</p>
        <p>The Research Team</p>
        """
    )
