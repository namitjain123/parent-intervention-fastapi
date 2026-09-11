from datetime import datetime, timedelta, timezone

from fastapi import BackgroundTasks, HTTPException
from sqlalchemy.orm import Session

from app.class_flow_config import resolve_flow
from app.core.config import settings
from app.models import User
from app.services.email_service_classflow import send_class_b_lock_email


def _send_lock_email(email: str):
    try:
        send_class_b_lock_email(email)
        print(f"Lock email sent to {email}")
    except Exception as e:
        print(f"Lock email failed for {email}: {e}")


def _get_user_or_404(db: Session, participant_id: str) -> User:
    db_user = db.query(User).filter(User.azure_id == participant_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


def complete_pre_questionnaire(
    db: Session,
    participant_id: str,
    grade: str,
    teacher: str,
    background_tasks: BackgroundTasks,
) -> User:
    db_user = _get_user_or_404(db, participant_id)

    if not grade or not teacher:
        raise HTTPException(status_code=400, detail="grade and teacher are required")

    try:
        selected_class, teacher_name = resolve_flow(grade, teacher)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    db_user.pre_questionnaire_completed = True
    db_user.user_class = selected_class
    db_user.grade = grade.strip()
    db_user.teacher_code = teacher.strip()
    db_user.teacher_name = teacher_name

    if selected_class == "A":
        db_user.delayed_survey_unlocked = False
        db_user.delayed_survey_completed = False
        db_user.delayed_unlock_at = None
        db_user.lock_email_sent_at = None
        db_user.unlock_email_sent_at = None

        if db_user.current_episode == 0:
            db_user.current_episode = 1

    elif selected_class == "B":
        now = datetime.now(timezone.utc)

        db_user.delayed_survey_unlocked = False
        db_user.delayed_survey_completed = False
        db_user.delayed_unlock_at = now + timedelta(
            minutes=settings.DELAYED_SURVEY_UNLOCK_MINUTES
        )
        db_user.current_episode = 0

        if not db_user.lock_email_sent_at:
            # Sent after the response goes out, not inline: a send can take
            # up to a minute if Azure is slow or throttling, and the
            # participant's "Completing pre-questionnaire" page - and this
            # commit - would sit waiting on it.
            background_tasks.add_task(_send_lock_email, db_user.email)
            db_user.lock_email_sent_at = now

        db_user.unlock_email_sent_at = None

    db.commit()
    return db_user


def complete_delayed_survey(db: Session, participant_id: str) -> User:
    db_user = _get_user_or_404(db, participant_id)

    if db_user.user_class != "B":
        raise HTTPException(status_code=400, detail="User is not in Class B")

    if not db_user.delayed_survey_unlocked:
        raise HTTPException(status_code=400, detail="Delayed survey is still locked")

    db_user.delayed_survey_completed = True

    if db_user.current_episode == 0:
        db_user.current_episode = 1

    db.commit()
    return db_user


def complete_post_questionnaire(db: Session, participant_id: str) -> User:
    db_user = _get_user_or_404(db, participant_id)

    db_user.post_questionnaire_completed = True
    db.commit()
    return db_user


def get_survey_access_status(user: User) -> dict:
    if not user.pre_questionnaire_completed:
        return {
            "pre_questionnaire_completed": False,
            "user_class": user.user_class,
            "locked": True,
            "show_delayed_survey": False,
            "episodes_open": False,
            "message": "Complete pre-questionnaire first",
        }

    if user.user_class == "A":
        return {
            "pre_questionnaire_completed": True,
            "user_class": "A",
            "locked": False,
            "show_delayed_survey": False,
            "episodes_open": True,
            "message": "Episodes available",
        }

    if user.user_class == "B":
        if not user.delayed_survey_unlocked:
            return {
                "pre_questionnaire_completed": True,
                "user_class": "B",
                "locked": True,
                "show_delayed_survey": False,
                "episodes_open": False,
                "delayed_unlock_at": user.delayed_unlock_at,
                "message": "Delayed survey is still locked",
            }

        if user.delayed_survey_unlocked and not user.delayed_survey_completed:
            return {
                "pre_questionnaire_completed": True,
                "user_class": "B",
                "locked": False,
                "show_delayed_survey": True,
                "episodes_open": False,
                "delayed_unlock_at": user.delayed_unlock_at,
                "message": "Delayed survey is now open",
            }

        return {
            "pre_questionnaire_completed": True,
            "user_class": "B",
            "locked": False,
            "show_delayed_survey": False,
            "episodes_open": True,
            "delayed_unlock_at": user.delayed_unlock_at,
            "message": "Episodes available",
        }

    return {
        "pre_questionnaire_completed": user.pre_questionnaire_completed,
        "user_class": user.user_class,
        "locked": True,
        "show_delayed_survey": False,
        "episodes_open": False,
        "message": "User class not set",
    }
