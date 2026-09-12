from app.db.session import SessionLocal
from app.services.reminder_service import (
    get_users_needing_form_reminder,
    mark_reminder_sent,
)
from app.services.email_service import send_reminder_email


def run():
    db = SessionLocal()
    try:
        inactivity_users = get_users_needing_form_reminder(db)
        print(f"Found {len(inactivity_users)} users needing inactivity reminders")

        for user in inactivity_users:
            print(f"Sending inactivity reminder to {user.email}")
            result = send_reminder_email(user.email, user.name)
            print("Send result:", result)
            mark_reminder_sent(user, db)

    finally:
        db.close()


if __name__ == "__main__":
    run()
