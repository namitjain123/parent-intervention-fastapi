from datetime import datetime, timedelta, timezone
from models import User, UserEpisodeProgress


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


def get_users_needing_25day_progress_reminder(db):
    now = datetime.now(timezone.utc)
    progress_cutoff = now - timedelta(days=25)

    candidate_users = db.query(User).filter(
        User.post_questionnaire_completed == False,
        User.created_at <= progress_cutoff,
        User.midway_reminder_sent_at == None
    ).all()

    eligible_users = []

    for user in candidate_users:
        completed_count = db.query(UserEpisodeProgress).filter(
            UserEpisodeProgress.user_id == user.id,
            UserEpisodeProgress.completed == True
        ).count()

        if completed_count < 4:   # less than 50% of 8 episodes
            eligible_users.append(user)

    return eligible_users


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