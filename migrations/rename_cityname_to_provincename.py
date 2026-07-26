import sqlite3
from pathlib import Path


def get_db_path() -> Path:
    project_root = Path(__file__).resolve().parents[1]
    return project_root / "instance" / "urac_account.db"


def column_names(connection: sqlite3.Connection, table_name: str) -> set[str]:
    rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {row[1] for row in rows}


def migrate() -> None:
    db_path = get_db_path()
    if not db_path.exists():
        print(f"Database not found: {db_path}")
        return

    connection = sqlite3.connect(db_path)
    try:
        columns = column_names(connection, "locations")
        if not columns:
            print("Table 'locations' does not exist. Nothing to migrate.")
            return

        if "ProvinceName" in columns:
            print("Column 'ProvinceName' already exists. Nothing to migrate.")
            return

        if "CityName" not in columns:
            print("Column 'CityName' not found. Nothing to migrate.")
            return

        connection.execute("ALTER TABLE locations RENAME COLUMN CityName TO ProvinceName")
        connection.commit()
        print("Migration successful: locations.CityName -> locations.ProvinceName")
    finally:
        connection.close()


if __name__ == "__main__":
    migrate()
