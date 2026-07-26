import sqlite3
from pathlib import Path


def get_db_path() -> Path:
    project_root = Path(__file__).resolve().parents[1]
    return project_root / "instance" / "urac_account.db"


def column_names(connection: sqlite3.Connection, table_name: str) -> set[str]:
    rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {row[1] for row in rows}


def rollback() -> None:
    db_path = get_db_path()
    if not db_path.exists():
        print(f"Database not found: {db_path}")
        return

    connection = sqlite3.connect(db_path)
    try:
        columns = column_names(connection, "locations")
        if not columns:
            print("Table 'locations' does not exist. Nothing to rollback.")
            return

        if "CityName" in columns:
            print("Column 'CityName' already exists. Nothing to rollback.")
            return

        if "ProvinceName" not in columns:
            print("Column 'ProvinceName' not found. Nothing to rollback.")
            return

        connection.execute("ALTER TABLE locations RENAME COLUMN ProvinceName TO CityName")
        connection.commit()
        print("Rollback successful: locations.ProvinceName -> locations.CityName")
    finally:
        connection.close()


if __name__ == "__main__":
    rollback()
