import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))


@pytest.fixture(scope="session")
def db_path(tmp_path_factory):
    """Build a fresh copy of the database for the test run."""
    from load_data import build_database

    path = tmp_path_factory.mktemp("db") / "test_league.db"
    build_database(path)
    return path
