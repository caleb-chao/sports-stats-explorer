"""
Build the SQLite database from the CSV files in data/raw/.

Run this any time the CSVs or db/schema.sql change:
    python scripts/load_data.py

It creates db/league.db (ignored by git -- everyone builds their own copy).
"""

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from sports_stats.db import DB_PATH, get_connection  # noqa: E402

RAW_DIR = ROOT / "data" / "raw"
SCHEMA_PATH = ROOT / "db" / "schema.sql"

# Order matters: tables that are referenced by others get loaded first.
TABLES = ["teams", "players", "games", "player_game_stats"]


def build_database(db_path: Path = DB_PATH) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with get_connection(db_path) as conn:
        conn.executescript(SCHEMA_PATH.read_text())
        for table in TABLES:
            csv_path = RAW_DIR / f"{table}.csv"
            df = pd.read_csv(csv_path)
            df.to_sql(table, conn, if_exists="append", index=False)
            print(f"  loaded {len(df):>5} rows into {table}")
    print(f"Database ready at {db_path}")


if __name__ == "__main__":
    build_database()
