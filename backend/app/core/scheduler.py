from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings
from app.db.session import SessionLocal
from app.services.email_service import (
    send_reminder_email,
    send_25day_progress_reminder,
    send_pre_survey_reminder_email,
    send_post_survey_reminder_email,
)
from app.services.episode_access import process_delayed_survey_unlocks
from app.services.reminder_service import (
    get_users_needing_form_reminder,
    get_users_needing_25day_progress_reminder,
    get_users_needing_pre_survey_reminder,
    get_users_needing_post_survey_reminder,
    mark_reminder_sent,
    mark_midway_reminder_sent,
    mark_pre_survey_reminder_sent,
    mark_post_survey_reminder_sent,
)

scheduler = BackgroundScheduler()


def scheduled_process_delayed_unlocks():
    db = SessionLocal()
    try:
        process_delayed_survey_unlocks(db)
    finally:
        db.close()


def scheduled_send_inactivity_reminders():
    db = SessionLocal()
    try:
        users = get_users_needing_form_reminder(db)
        print(f"[Reminder] Found {len(users)} users needing inactivity reminders")
        for user in users:
            try:
                send_reminder_email(user.email, user.name)
                print(f"[Reminder] Inactivity email sent to {user.email}")
            except Exception as e:
                print(f"[Reminder] Inactivity email failed for {user.email}: {e}")
            mark_reminder_sent(user, db)
    finally:
        db.close()


def scheduled_send_25day_reminders():
    db = SessionLocal()
    try:
        users = get_users_needing_25day_progress_reminder(db)
        print(f"[Reminder] Found {len(users)} users needing 25-day progress reminders")
        for user in users:
            try:
                send_25day_progress_reminder(user.email, user.name)
                print(f"[Reminder] 25-day email sent to {user.email}")
            except Exception as e:
                print(f"[Reminder] 25-day email failed for {user.email}: {e}")
            mark_midway_reminder_sent(user, db)
    finally:
        db.close()


def scheduled_send_pre_survey_reminders():
    db = SessionLocal()
    try:
        users = get_users_needing_pre_survey_reminder(db)
        print(f"[Reminder] Found {len(users)} users needing pre-survey reminders")
        for user in users:
            reminder_number = (user.pre_survey_reminder_count or 0) + 1
            try:
                send_pre_survey_reminder_email(user.email, user.name, reminder_number)
                print(f"[Reminder] Pre-survey reminder {reminder_number} sent to {user.email}")
            except Exception as e:
                print(f"[Reminder] Pre-survey reminder failed for {user.email}: {e}")
            mark_pre_survey_reminder_sent(user, db)
    finally:
        db.close()


def scheduled_send_post_survey_reminders():
    db = SessionLocal()
    try:
        users = get_users_needing_post_survey_reminder(db)
        print(f"[Reminder] Found {len(users)} users needing post-survey reminders")
        for user in users:
            reminder_number = (user.post_survey_reminder_count or 0) + 1
            try:
                send_post_survey_reminder_email(user.email, user.name, reminder_number)
                print(f"[Reminder] Post-survey reminder {reminder_number} sent to {user.email}")
            except Exception as e:
                print(f"[Reminder] Post-survey reminder failed for {user.email}: {e}")
            mark_post_survey_reminder_sent(user, db)
    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(
        scheduled_process_delayed_unlocks,
        "interval",
        minutes=settings.DELAYED_UNLOCK_JOB_INTERVAL_MINUTES,
        id="delayed_survey_unlock_job",
        replace_existing=True,
    )
    # TODO: change minutes=10 to days=1 after testing
    scheduler.add_job(
        scheduled_send_inactivity_reminders,
        "interval",
        minutes=settings.INACTIVITY_REMINDER_JOB_INTERVAL_MINUTES,
        id="inactivity_reminder_job",
        replace_existing=True,
    )
    scheduler.add_job(
        scheduled_send_25day_reminders,
        "interval",
        minutes=settings.PROGRESS_REMINDER_JOB_INTERVAL_MINUTES,
        id="25day_progress_reminder_job",
        replace_existing=True,
    )
    scheduler.add_job(
        scheduled_send_pre_survey_reminders,
        "interval",
        minutes=settings.PRE_SURVEY_REMINDER_JOB_INTERVAL_MINUTES,
        id="pre_survey_reminder_job",
        replace_existing=True,
    )
    scheduler.add_job(
        scheduled_send_post_survey_reminders,
        "interval",
        minutes=settings.POST_SURVEY_REMINDER_JOB_INTERVAL_MINUTES,
        id="post_survey_reminder_job",
        replace_existing=True,
    )
    scheduler.start()
    print("Scheduler started")


def stop_scheduler():
    scheduler.shutdown()
    print("Scheduler stopped")
