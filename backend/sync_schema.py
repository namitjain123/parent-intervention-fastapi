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


def default_clause(column) -> str:
    """
    Return " DEFAULT <value>" for a column with a simple literal Integer or
    Boolean default (e.g. Column(Integer, default=0)), so pre-existing rows
    get that value on ALTER instead of NULL.

    This matters because "NULL < N" is NULL in SQL, not True - a WHERE clause
    treats that as no match, not as "0 < N". A counter column left NULL by a
    plain ALTER TABLE silently and permanently excludes every pre-existing
    row from any query that compares it with "<", even when it's obviously
    overdue. This bit the pre-survey and post-survey reminder counters.

    Returns "" for columns without a simple literal default (e.g. DateTime
    columns, whose default is usually a callable like `lambda: datetime.now()`)
    - NULL is the semantically correct value for those on old rows, since the
    event they track genuinely never happened for that row.
    """
    default = column.default
    if default is None or getattr(default, "is_callable", True):
        return ""

    value = default.arg
    if isinstance(value, bool):
        return f" DEFAULT {1 if value else 0}"
    if isinstance(value, int):
        return f" DEFAULT {value}"
    return ""


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
        # without a default would fail to add. Where the model has a simple
        # literal default (e.g. Integer default=0), apply it via DEFAULT so
        # pre-existing rows get that value instead of NULL - see default_clause().
        stmt = f'ALTER TABLE {table_name} ADD COLUMN {column.name} {column_type}{default_clause(column)}'
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