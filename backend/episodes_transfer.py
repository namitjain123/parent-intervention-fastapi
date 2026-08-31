"""
Copy episode rows between databases (e.g. local -> production).

Audio and transcripts already live in Azure Blob Storage and are referenced by
absolute, publicly readable URLs, so only the database ROWS need to move. No
media is re-uploaded and no blob is duplicated.

Rows are matched on episode_number: an existing episode is updated in place, a
new one is inserted. Nothing is ever deleted.

Typical local -> production flow:

    # 1. on your machine (reads the DB in backend/.env)
    python episodes_transfer.py export

    # 2. commit episodes_export.json and push, wait for the deploy

    # 3. in the App Service SSH console, where DATABASE_URL already points at prod
    cd /tmp/<hash>
    python episodes_transfer.py import           # dry run - shows what would change
    python episodes_transfer.py import --apply   # write the rows
"""

import json
import os
import sys

from app.db.session import SessionLocal
from app.models import Episode

EXPORT_FILE = "episodes_export.json"

# Columns worth carrying across. 'id' is database-specific and 'created_at'
# is left to default on the target, so neither is copied.
FIELDS = [
    "episode_number",
    "title",
    "description",
    "audio_url",
    "transcript_url",
    "transcript_text",
    "quiz_json",
    "is_published",
]


def export_episodes():
    db = SessionLocal()
    try:
        episodes = db.query(Episode).order_by(Episode.episode_number).all()
        payload = [{f: getattr(ep, f) for f in FIELDS} for ep in episodes]
    finally:
        db.close()

    with open(EXPORT_FILE, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)

    size_kb = os.path.getsize(EXPORT_FILE) / 1024
    print(f"Exported {len(payload)} episode(s) to {EXPORT_FILE} ({size_kb:.1f} KB)")
    for ep in payload:
        print(f"  #{ep['episode_number']}: {ep['title']!r}")


def import_episodes(apply_changes: bool):
    if not os.path.exists(EXPORT_FILE):
        sys.exit(f"{EXPORT_FILE} not found. Run 'python episodes_transfer.py export' first.")

    with open(EXPORT_FILE, encoding="utf-8") as fh:
        payload = json.load(fh)

    db = SessionLocal()
    try:
        to_insert, to_update = [], []

        for row in payload:
            existing = (
                db.query(Episode)
                .filter(Episode.episode_number == row["episode_number"])
                .first()
            )
            (to_update if existing else to_insert).append((row, existing))

        print(f"{len(to_insert)} to insert, {len(to_update)} to update\n")
        for row, _ in to_insert:
            print(f"  INSERT #{row['episode_number']}: {row['title']!r}")
        for row, _ in to_update:
            print(f"  UPDATE #{row['episode_number']}: {row['title']!r}")

        if not apply_changes:
            print("\nDry run. Re-run with --apply to write these rows.")
            return

        for row, existing in to_update:
            for field, value in row.items():
                setattr(existing, field, value)

        for row, _ in to_insert:
            db.add(Episode(**row))

        db.commit()
        print(f"\nDone. {len(to_insert)} inserted, {len(to_update)} updated.")
    finally:
        db.close()


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else ""

    if command == "export":
        export_episodes()
    elif command == "import":
        import_episodes(apply_changes="--apply" in sys.argv)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
