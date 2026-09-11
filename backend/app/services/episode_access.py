from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models import User
from app.services.email_service_classflow import (
    send_class_b_lock_email,
    send_class_b_unlock_email,
)


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


def send_pending_lock_emails(db: Session):
    """
    Send the "episodes will open soon" email to Class B participants still
    waiting for their unlock who haven't had it yet.

    This used to be sent once, inline, when the pre-questionnaire completed,
    and was marked as sent whether or not it went out - so an Azure throttle
    or a restart mid-send lost it for good. Run from the scheduler instead and
    only marked on success, a failed send is simply retried next cycle.
    """
    users = (
        db.query(User)
        .filter(
            User.user_class == "B",
            User.delayed_survey_unlocked == False,
            User.lock_email_sent_at.is_(None),
        )
        .all()
    )

    for user in users:
        try:
            send_class_b_lock_email(user.email)
            user.lock_email_sent_at = datetime.now(timezone.utc)
            db.commit()
            print(f"Lock email sent to {user.email}")
        except Exception as e:
            db.rollback()
            print(f"Lock email failed for {user.email}: {e} - will retry next cycle")


def process_delayed_survey_unlocks(db: Session):
    now = datetime.now(timezone.utc)

    # Unlock anyone whose wait is over, and retry the unlock email for anyone
    # already unlocked whose email hasn't gone out yet (until they've done the
    # delayed survey, after which "episodes are now open" is moot).
    users = (
        db.query(User)
        .filter(
            User.user_class == "B",
            or_(
                and_(
                    User.delayed_survey_unlocked == False,
                    User.delayed_unlock_at.isnot(None),
                    User.delayed_unlock_at <= now,
                ),
                and_(
                    User.delayed_survey_unlocked == True,
                    User.delayed_survey_completed == False,
                    User.unlock_email_sent_at.is_(None),
                ),
            ),
        )
        .all()
    )

    updated_users = []

    for user in users:
        if not user.delayed_survey_unlocked:
            user.delayed_survey_unlocked = True
            updated_users.append(user.email)
            # Save the unlock itself even if the email below fails.
            db.commit()

        # Marked only once Azure accepts it - a throttled send is retried on
        # the next cycle rather than being lost.
        try:
            send_class_b_unlock_email(user.email)
            user.unlock_email_sent_at = now
            db.commit()
            print(f"Unlock email sent to {user.email}")
        except Exception as e:
            db.rollback()
            print(f"Unlock email failed for {user.email}: {e} - will retry next cycle")

    return {
        "message": "Processed delayed survey unlocks",
        "updated_count": len(updated_users),
        "updated_users": updated_users,
    }
