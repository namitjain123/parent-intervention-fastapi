from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import User
from app.services.email_service_classflow import send_class_b_unlock_email


def ensure_episode_access(db_user: User, episode_number: int):
    if not db_user.pre_questionnaire_completed:
        raise HTTPException(status_code=403, detail="Complete pre-questionnaire first")

    if db_user.user_class == "B":
        if not db_user.delayed_survey_unlocked:
            raise HTTPException(
                status_code=403,
                detail="Delayed survey is still locked. Please come back later.",
            )

        if not db_user.delayed_survey_completed:
            raise HTTPException(
                status_code=403,
                detail="Complete delayed survey first.",
            )

    if episode_number > db_user.current_episode:
        raise HTTPException(status_code=403, detail="Episode is locked")


def process_delayed_survey_unlocks(db: Session):
    now = datetime.now(timezone.utc)

    users = (
        db.query(User)
        .filter(
            User.user_class == "B",
            User.delayed_survey_unlocked == False,
            User.delayed_unlock_at.isnot(None),
            User.delayed_unlock_at <= now,
        )
        .all()
    )

    updated_users = []

    for user in users:
        user.delayed_survey_unlocked = True

        if not user.unlock_email_sent_at:
            try:
                send_class_b_unlock_email(user.email)
                print(f"Unlock email sent to {user.email}")
            except Exception as e:
                print(f"Unlock email failed for {user.email}: {e}")

            # IMPORTANT: mark timestamp even if email fails,
            # so Azure rate limit does not spam every minute.
            user.unlock_email_sent_at = now

        updated_users.append(user.email)

    if users:
        db.commit()

    return {
        "message": "Processed delayed survey unlocks",
        "updated_count": len(updated_users),
        "updated_users": updated_users,
    }
