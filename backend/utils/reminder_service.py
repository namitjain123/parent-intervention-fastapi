from datetime import datetime, timedelta, timezone
from models import User

from datetime import datetime, timedelta, timezone
from models import User

def get_users_needing_form_reminder(db):
    now = datetime.now(timezone.utc)
    inactivity_cutoff = now - timedelta(days=7)
    reminder_cutoff = now - timedelta(days=7)

    users = db.query(User).filter(
        User.post_questionnaire_completed == False,
        User.last_activity_at <= inactivity_cutoff,
        (
            (User.last_reminder_sent_at == None) |
            (User.last_reminder_sent_at <= reminder_cutoff)
        )
    ).all()

    return users

def mark_reminder_sent(user, db):
    from datetime import datetime, timezone

    user.last_reminder_sent_at = datetime.now(timezone.utc)
    user.reminder_count = (user.reminder_count or 0) + 1
    db.commit()
    db.refresh(user)