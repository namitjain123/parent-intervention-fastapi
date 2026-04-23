from dotenv import load_dotenv
load_dotenv()

from database import SessionLocal
from utils.reminder_service import (
    get_users_needing_form_reminder,
    get_users_needing_25day_progress_reminder,
    mark_reminder_sent,
    mark_midway_reminder_sent,
)
from utils.email_service import (
    send_reminder_email,
    send_25day_progress_reminder,
)


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

        progress_users = get_users_needing_25day_progress_reminder(db)
        print(f"Found {len(progress_users)} users needing 25-day progress reminders")

        for user in progress_users:
            print(f"Sending 25-day progress reminder to {user.email}")
            result = send_25day_progress_reminder(user.email, user.name)
            print("Send result:", result)
            mark_midway_reminder_sent(user, db)

    finally:
        db.close()


if __name__ == "__main__":
    run()