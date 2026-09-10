from datetime import datetime, timedelta, timezone
from app.core.config import settings
from app.models import User


def get_users_needing_form_reminder(db):
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=settings.INACTIVITY_REMINDER_INTERVAL_MINUTES)

    users = db.query(User).filter(
        User.post_questionnaire_completed == False,
        User.last_activity_at <= cutoff,
        (
            (User.last_reminder_sent_at == None) |
            (User.last_reminder_sent_at <= cutoff)
        )
    ).all()

    return users


def get_users_needing_25day_progress_reminder(db):
    now = datetime.now(timezone.utc)
    progress_cutoff = now - timedelta(minutes=settings.PROGRESS_REMINDER_INTERVAL_MINUTES)

    users = db.query(User).filter(
        User.post_questionnaire_completed == False,
        User.created_at <= progress_cutoff,
        User.midway_reminder_sent_at == None
    ).all()

    return users


def mark_reminder_sent(user, db):
    user.last_reminder_sent_at = datetime.now(timezone.utc)
    user.reminder_count = (user.reminder_count or 0) + 1
    db.commit()
    db.refresh(user)


def mark_midway_reminder_sent(user, db):
    user.midway_reminder_sent_at = datetime.now(timezone.utc)
    user.reminder_count = (user.reminder_count or 0) + 1
    db.commit()
    db.refresh(user)


def get_users_needing_pre_survey_reminder(db):
    """
    Registered (a User row exists) but never completed the pre-questionnaire.
    Reminded every PRE_SURVEY_REMINDER_INTERVAL_DAYS since registration (or
    since their last reminder), up to PRE_SURVEY_REMINDER_MAX_COUNT times.
    """
    now = datetime.now(timezone.utc)
    interval_cutoff = now - timedelta(minutes=settings.PRE_SURVEY_REMINDER_INTERVAL_MINUTES)

    users = db.query(User).filter(
        User.pre_questionnaire_completed == False,
        User.pre_survey_reminder_count < settings.PRE_SURVEY_REMINDER_MAX_COUNT,
        (
            (User.last_pre_survey_reminder_sent_at == None) &
            (User.created_at <= interval_cutoff)
        ) | (User.last_pre_survey_reminder_sent_at <= interval_cutoff)
    ).all()

    return users


def mark_pre_survey_reminder_sent(user, db):
    user.last_pre_survey_reminder_sent_at = datetime.now(timezone.utc)
    user.pre_survey_reminder_count = (user.pre_survey_reminder_count or 0) + 1
    db.commit()
    db.refresh(user)


def get_users_needing_post_survey_reminder(db):
    """
    Completed all episodes (all_episodes_completed_at is set) but never
    completed the post-questionnaire. Reminded every
    POST_SURVEY_REMINDER_INTERVAL_MINUTES since finishing the last episode
    (or since their last reminder), up to POST_SURVEY_REMINDER_MAX_COUNT times.
    """
    now = datetime.now(timezone.utc)
    interval_cutoff = now - timedelta(minutes=settings.POST_SURVEY_REMINDER_INTERVAL_MINUTES)

    users = db.query(User).filter(
        User.post_questionnaire_completed == False,
        User.post_survey_reminder_count < settings.POST_SURVEY_REMINDER_MAX_COUNT,
        User.all_episodes_completed_at.isnot(None),
        User.all_episodes_completed_at <= interval_cutoff,
        (
            (User.last_post_survey_reminder_sent_at == None) |
            (User.last_post_survey_reminder_sent_at <= interval_cutoff)
        )
    ).all()

    return users


def mark_post_survey_reminder_sent(user, db):
    user.last_post_survey_reminder_sent_at = datetime.now(timezone.utc)
    user.post_survey_reminder_count = (user.post_survey_reminder_count or 0) + 1
    db.commit()
    db.refresh(user)
