"""
Database helpers. You usually only need `run_query`:

    from sports_stats.db import run_query
    df = run_query("top_scorers", {"limit": 10})

That reads sql/top_scorers.sql, runs it against db/league.db, and returns a
pandas DataFrame. Named parameters in the SQL look like `:limit`.
"""

import re
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "db" / "league.db"
SQL_DIR = ROOT / "sql"


class QueryNotImplemented(Exception):
    """Raised when a .sql file exists but has no SQL in it yet (only comments)."""


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    return sqlite3.connect(db_path)


def load_sql(name: str) -> str:
    """Return the text of sql/<name>.sql."""
    return (SQL_DIR / f"{name}.sql").read_text()


def is_implemented(sql: str) -> bool:
    """True if the SQL has something other than comments and whitespace."""
    without_comments = re.sub(r"--.*", "", sql)
    return bool(without_comments.strip())


def run_query(name: str, params: dict | None = None, db_path: Path = DB_PATH) -> pd.DataFrame:
    """Run sql/<name>.sql and return the result as a DataFrame."""
    sql = load_sql(name)
    if not is_implemented(sql):
        raise QueryNotImplemented(f"sql/{name}.sql has no query yet")
    if not db_path.exists():
        raise FileNotFoundError(
            f"{db_path} not found. Build it first with: python scripts/load_data.py"
        )
    with get_connection(db_path) as conn:
        return pd.read_sql_query(sql, conn, params=params or {})
