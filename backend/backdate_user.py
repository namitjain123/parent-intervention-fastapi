"""
Backdate a single user's timestamps so the reminder jobs will pick them up.

The reminder emails only fire for users who cross real time thresholds
(7 days inactive, 21 days since signup), so there is no way to exercise them
without either waiting weeks or moving a test user's clock back. This does the
latter, for ONE explicitly named user at a time.

    WARNING: only ever run this against a TEST account. Backdating a real
    participant's created_at or last_activity_at corrupts study timing data.

Qualifying conditions (see app/services/reminder_service.py):

  inactivity reminder  post_questionnaire_completed = False
                       last_activity_at   <= now - 7 days
                       last_reminder_sent_at IS NULL or <= now - 7 days

  progress reminder    post_questionnaire_completed = False
                       created_at         <= now - 21 days
                       midway_reminder_sent_at IS NULL

Usage:

    python backdate_user.py --list                        # who is eligible right now
    python backdate_user.py --email you@example.com --status
    python backdate_user.py --email you@example.com --inactive
    python backdate_user.py --email you@example.com --old-account
    python backdate_user.py --email you@example.com --both --apply
"""

import argparse
from datetime import datetime, timedelta, timezone

from app.db.session import SessionLocal
from app.models import User
from app.services.reminder_service import (
    get_users_needing_form_reminder,
    get_users_needing_25day_progress_reminder,
)


def show_eligible(db):
    inactivity = get_users_needing_form_reminder(db)
    progress = get_users_needing_25day_progress_reminder(db)

    print(f"Eligible for INACTIVITY reminder ({len(inactivity)}):")
    for u in inactivity:
        print(f"  {u.email}  last_activity={u.last_activity_at}")

    print(f"\nEligible for PROGRESS reminder ({len(progress)}):")
    for u in progress:
        print(f"  {u.email}  created_at={u.created_at}")


def show_status(user: User):
    now = datetime.now(timezone.utc)

    def ago(ts):
        if ts is None:
            return "never"
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        return f"{(now - ts).days}d ago"

    print(f"\n{user.email}")
    print(f"  post_questionnaire_completed : {user.post_questionnaire_completed}  (must be False)")
    print(f"  last_activity_at             : {ago(user.last_activity_at)}  (needs >= 7d)")
    print(f"  last_reminder_sent_at        : {ago(user.last_reminder_sent_at)}  (needs never or >= 7d)")
    print(f"  created_at                   : {ago(user.created_at)}  (needs >= 21d)")
    print(f"  midway_reminder_sent_at      : {ago(user.midway_reminder_sent_at)}  (must be never)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--email", help="email of the TEST user to backdate")
    parser.add_argument("--list", action="store_true", help="show who is currently eligible")
    parser.add_argument("--status", action="store_true", help="show one user's timestamps")
    parser.add_argument("--inactive", action="store_true", help="make eligible for the 7-day inactivity reminder")
    parser.add_argument("--old-account", action="store_true", help="make eligible for the 21-day progress reminder")
    parser.add_argument("--both", action="store_true", help="both of the above")
    parser.add_argument("--apply", action="store_true", help="actually write the changes")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        if args.list:
            show_eligible(db)
            return

        if not args.email:
            parser.error("--email is required (or use --list)")

        user = db.query(User).filter(User.email == args.email).first()
        if not user:
            print(f"No user with email {args.email!r}")
            return

        if args.status:
            show_status(user)
            return

        want_inactive = args.inactive or args.both
        want_old = args.old_account or args.both

        if not (want_inactive or want_old):
            parser.error("pass --inactive, --old-account or --both")

        now = datetime.now(timezone.utc)
        changes = {}

        if want_inactive:
            # 8 days clears the 7-day threshold with a margin
            changes["last_activity_at"] = now - timedelta(days=8)
            changes["last_reminder_sent_at"] = None

        if want_old:
            # 22 days clears the 21-day threshold with a margin
            changes["created_at"] = now - timedelta(days=22)
            changes["midway_reminder_sent_at"] = None

        # Both reminders require this to be False
        changes["post_questionnaire_completed"] = False

        print(f"\n{user.email} - planned changes:")
        for field, value in changes.items():
            print(f"  {field}: {getattr(user, field)!r} -> {value!r}")

        if not args.apply:
            print("\nDry run. Re-run with --apply to write.")
            return

        for field, value in changes.items():
            setattr(user, field, value)
        db.commit()

        print("\nApplied. Now run:  python send_reminder.py")
    finally:
        db.close()


if __name__ == "__main__":
    main()
