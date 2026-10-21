"""
Tests for the SQL queries. Run with:  pytest

Tests for TODO queries are SKIPPED until the .sql file has a query in it.
Once you write the query, the test runs automatically -- make it pass!
"""

import pytest

from sports_stats.db import is_implemented, load_sql, run_query


def run_or_skip(name, db_path, params=None):
    if not is_implemented(load_sql(name)):
        pytest.skip(f"sql/{name}.sql not written yet")
    return run_query(name, params, db_path=db_path)


# --- Worked example -------------------------------------------------------

def test_top_scorers(db_path):
    df = run_query("top_scorers", {"limit": 10, "min_games": 1}, db_path=db_path)
    assert list(df.columns) == ["player", "team", "games", "total_points", "points_per_game"]
    assert len(df) == 10
    # Sorted best first
    assert df["points_per_game"].is_monotonic_decreasing


# --- TODO queries ---------------------------------------------------------

def test_team_standings(db_path):
    df = run_or_skip("team_standings", db_path)
    assert {"team", "wins", "losses", "win_pct"} <= set(df.columns)
    assert len(df) == 8  # one row per team
    # Every game has exactly one winner and one loser.
    assert df["wins"].sum() == df["losses"].sum()
    assert df["win_pct"].is_monotonic_decreasing


def test_close_games(db_path):
    df = run_or_skip("close_games", db_path, {"margin": 5})
    assert {"team", "close_games", "close_wins", "close_losses"} <= set(df.columns)
    assert (df["close_wins"] + df["close_losses"] == df["close_games"]).all()


def test_player_profile(db_path):
    name = run_query("top_scorers", {"limit": 1, "min_games": 1}, db_path=db_path)["player"][0]
    df = run_or_skip("player_profile", db_path, {"player_name": name})
    assert {"game_date", "opponent", "points"} <= set(df.columns)
    assert len(df) > 0
    assert df["game_date"].is_monotonic_increasing
