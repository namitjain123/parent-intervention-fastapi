from dotenv import load_dotenv
load_dotenv()

from database import SessionLocal
from utils.reminder_service import get_users_needing_form_reminder, mark_reminder_sent
from utils.email_service import send_reminder_email

def run():
    db = SessionLocal()
    try:
        users = get_users_needing_form_reminder(db)
        print(f"Found {len(users)} users needing reminders")

        for user in users:
            print(f"Sending reminder to {user.email}")
            result = send_reminder_email(user.email, user.name)
            print("Send result:", result)
            mark_reminder_sent(user, db)

    finally:
        db.close()

if __name__ == "__main__":
    run()