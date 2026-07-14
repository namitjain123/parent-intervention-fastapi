"""
One-off migration: add grade / teacher_code / teacher_name columns to users.

Historical script, kept for reference. New schema changes should use Alembic
instead (see alembic/ and `alembic revision --autogenerate`), since
Base.metadata.create_all only creates missing TABLES, not missing COLUMNS.

Run from the backend/ directory:

    venv\\Scripts\\activate
    python migrate_add_grade_teacher.py
"""

from sqlalchemy import text
from app.db.session import engine

STATEMENTS = [
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS grade VARCHAR",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS teacher_code VARCHAR",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS teacher_name VARCHAR",
]


def run():
    with engine.begin() as conn:
        for stmt in STATEMENTS:
            print(f"Running: {stmt}")
            conn.execute(text(stmt))
    print("Migration complete.")


if __name__ == "__main__":
    run()
