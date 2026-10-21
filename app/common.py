"""
Shared setup for every page of the app. Each page starts with:

    from common import run_query_or_todo
"""

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from sports_stats.db import DB_PATH, QueryNotImplemented, run_query  # noqa: E402


@st.cache_resource
def ensure_database() -> None:
    """Build db/league.db from the CSVs if it doesn't exist (e.g. on first deploy)."""
    if not DB_PATH.exists():
        from load_data import build_database
        build_database()


@st.cache_data
def _cached_query(name: str, params: tuple):
    return run_query(name, dict(params))


def run_query_or_todo(name: str, params: dict | None = None):
    """
    Run sql/<name>.sql. If that file hasn't been written yet, show a friendly
    "TODO" box on the page instead of crashing, and return None.
    """
    ensure_database()
    try:
        return _cached_query(name, tuple(sorted((params or {}).items())))
    except QueryNotImplemented:
        st.info(
            f"🚧 **Not built yet.** Write the query in `sql/{name}.sql` "
            "(the hints are in that file), then refresh this page."
        )
        return None
