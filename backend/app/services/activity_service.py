from datetime import datetime, timezone


def update_user_activity(user, db):
    user.last_activity_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
