"""
Report (and optionally add) columns that exist in the SQLAlchemy models but are
missing from the actual database.

Base.metadata.create_all() creates missing TABLES but never adds missing COLUMNS
to a table that already exists, so a database created before a model gained new
columns will raise "UndefinedColumn" at query time. This script closes that gap.

It is additive only: it never drops or alters existing columns, and new columns
are always added as NULLable so existing rows stay valid.

Usage (from the backend/ directory, with DATABASE_URL pointing at the target DB):

    python sync_schema.py           # dry run - report what is missing
    python sync_schema.py --apply   # actually add the missing columns
"""

import sys

from sqlalchemy import inspect, text

from app.db.base import Base
from app.db.session import engine
import app.models  # noqa: F401  - registers the models on Base.metadata


def find_missing_columns():
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    missing = []

    for table_name, table in Base.metadata.tables.items():
        if table_name not in existing_tables:
            print(f"[table missing] {table_name} - create_all() will handle this one")
            continue

        db_columns = {col["name"] for col in inspector.get_columns(table_name)}

        for column in table.columns:
            if column.name not in db_columns:
                missing.append((table_name, column))

    return missing


def main():
    apply_changes = "--apply" in sys.argv

    missing = find_missing_columns()

    if not missing:
        print("Schema is in sync - no missing columns.")
        return

    print(f"\nFound {len(missing)} missing column(s):\n")

    statements = []
    for table_name, column in missing:
        column_type = column.type.compile(dialect=engine.dialect)
        # Always NULLable: the table may already hold rows, and a NOT NULL column
        # without a default would fail to add.
        stmt = f'ALTER TABLE {table_name} ADD COLUMN {column.name} {column_type}'
        statements.append(stmt)
        print(f"  {table_name}.{column.name}  ({column_type})")

    if not apply_changes:
        print("\nDry run. Re-run with --apply to execute:\n")
        for stmt in statements:
            print(f"  {stmt};")
        return

    print("\nApplying...")
    with engine.begin() as conn:
        for stmt in statements:
            print(f"  {stmt}")
            conn.execute(text(stmt))

    print("\nDone. Missing columns added.")


if __name__ == "__main__":
    main()
