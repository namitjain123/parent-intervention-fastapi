from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
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


def _claim_lock_email(db: Session, user_id: int) -> User | None:
    """
    Take ownership of sending this user's lock email, atomically.

    Two senders can reach the same user at once: the background task fired
    the moment they complete the pre-questionnaire, and the scheduler's
    catch-up sweep. Stamping lock_email_sent_at in a single conditional
    UPDATE means exactly one of them wins - the loser gets None back and does
    nothing, so nobody is emailed twice.
    """
    claimed = (
        db.query(User)
        .filter(User.id == user_id, User.lock_email_sent_at.is_(None))
        .update(
            {User.lock_email_sent_at: datetime.now(timezone.utc)},
            synchronize_session=False,
        )
    )
    db.commit()

    return db.get(User, user_id) if claimed else None


def _send_claimed_lock_email(db: Session, user: User) -> None:
    """Send a claimed lock email, releasing the claim again if it fails."""
    try:
        send_class_b_lock_email(user.email)
        print(f"Lock email sent to {user.email}")
    except Exception as e:
        db.query(User).filter(User.id == user.id).update(
            {User.lock_email_sent_at: None}, synchronize_session=False
        )
        db.commit()
        print(f"Lock email failed for {user.email}: {e} - will retry next cycle")


def send_lock_email_task(user_id: int) -> None:
    """
    Fired as a background task as soon as a Class B participant completes the
    pre-questionnaire, so the "episodes will open soon" email goes out right
    away instead of waiting for the scheduler's next sweep.

    Runs after the response, so the participant's page never waits on Azure,
    and opens its own session because the request's is already closed by then.
    """
    db = SessionLocal()
    try:
        user = _claim_lock_email(db, user_id)
        if user:
            _send_claimed_lock_email(db, user)
    finally:
        db.close()


def send_pending_lock_emails(db: Session):
    """
    Catch-up sweep for lock emails that never went out - Azure throttling, or
    a restart that killed the background task above. Marked as sent only once
    Azure accepts it, so a failure is retried next cycle.
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
        claimed = _claim_lock_email(db, user.id)
        if claimed:
            _send_claimed_lock_email(db, claimed)


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
