import os
import tempfile

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings
from app.db.session import SessionLocal
from app.services.email_service import (
    send_reminder_email,
    send_25day_progress_reminder,
    send_pre_survey_reminder_email,
    send_post_survey_reminder_email,
)
from app.services.episode_access import (
    process_delayed_survey_unlocks,
    send_pending_lock_emails,
)
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

# Held open for the life of the process that owns the scheduler.
_scheduler_lock_file = None


def _acquire_scheduler_lock() -> bool:
    """
    Gunicorn runs several worker processes (-w 2 in production), and each one
    runs the app's startup - so without this, every worker starts its own
    scheduler and every reminder email is sent once per worker. An exclusive
    non-blocking file lock lets exactly one process win. The OS releases it
    if that process dies, so a restarted worker can pick it back up.
    """
    global _scheduler_lock_file

    try:
        import fcntl
    except ImportError:
        # Windows (local dev) - a single uvicorn process, nothing to dedupe.
        return True

    lock_path = os.path.join(tempfile.gettempdir(), "parent_intervention_scheduler.lock")
    lock_file = open(lock_path, "w")
    try:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        lock_file.close()
        return False

    _scheduler_lock_file = lock_file
    return True


def scheduled_process_delayed_unlocks():
    db = SessionLocal()
    try:
        send_pending_lock_emails(db)
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
                mark_reminder_sent(user, db)  # only once Azure accepts it
                print(f"[Reminder] Inactivity email sent to {user.email}")
            except Exception as e:
                db.rollback()
                print(f"[Reminder] Inactivity email failed for {user.email}: {e} - will retry next cycle")
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
                mark_midway_reminder_sent(user, db)  # only once Azure accepts it
                print(f"[Reminder] 25-day email sent to {user.email}")
            except Exception as e:
                db.rollback()
                print(f"[Reminder] 25-day email failed for {user.email}: {e} - will retry next cycle")
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
                mark_pre_survey_reminder_sent(user, db)  # only once Azure accepts it
                print(f"[Reminder] Pre-survey reminder {reminder_number} sent to {user.email}")
            except Exception as e:
                db.rollback()
                print(f"[Reminder] Pre-survey reminder failed for {user.email}: {e} - will retry next cycle")
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
                mark_post_survey_reminder_sent(user, db)  # only once Azure accepts it
                print(f"[Reminder] Post-survey reminder {reminder_number} sent to {user.email}")
            except Exception as e:
                db.rollback()
                print(f"[Reminder] Post-survey reminder failed for {user.email}: {e} - will retry next cycle")
    finally:
        db.close()


def start_scheduler():
    if not _acquire_scheduler_lock():
        print(f"Scheduler already running in another worker - skipping in pid {os.getpid()}")
        return

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
    # Workers that lost the lock never started it; shutdown() would raise.
    if scheduler.running:
        scheduler.shutdown()
        print("Scheduler stopped")
