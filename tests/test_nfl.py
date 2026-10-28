from datetime import date
import sys
from pathlib import Path

import pytest

from sports_stats import nfl


def team(name, wins, losses, ties, pf, pa):
    return {"team": {"id": name, "displayName": name}, "stats": [
        {"name": k, "value": v} for k, v in dict(wins=wins, losses=losses, ties=ties, pointsFor=pf, pointsAgainst=pa).items()]}


def test_standings_ties_zero_games_and_tiebreak():
    payload = {"children": [{"standings": {"season": 2026, "seasonType": 2, "entries": [
        team("B", 1, 0, 1, 30, 20), team("A", 1, 0, 1, 40, 20), team("C", 0, 0, 0, 0, 0)]}}]}
    rows = nfl.parse_teams(payload, 2026)
    assert [r["team"] for r in rows] == ["A", "B", "C"]
    assert rows[0]["win_pct"] == .75
    assert rows[-1]["win_pct"] == 0
    with pytest.raises(ValueError, match="season"):
        nfl.parse_teams(payload, 2025)


def test_quarterbacks_filter_position_and_sort():
    payload = {"requestedSeason": {"year": 2026, "type": {"type": 2}}, "leaders": {"categories": [
        {"name": "passingYards", "leaders": [
            {"athlete": {"id": name, "displayName": name, "position": {"abbreviation": pos}},
             "team": {"displayName": "A"}, "value": yards}
            for name, pos, yards in [("Low", "QB", 50), ("High", "QB", 100), ("Receiver", "WR", 200)]]}]}}
    assert [r["player"] for r in nfl.parse_quarterbacks(payload, 2026)] == ["High", "Low"]
    with pytest.raises(ValueError, match="season"):
        nfl.parse_quarterbacks(payload, 2025)


def test_injuries_exclude_news_and_deduplicate_latest():
    payload = {"season": {"year": 2026}, "injuries": [{"id": "1", "displayName": "A", "injuries": [
        {"athlete": {"displayName": name}, "status": status, "date": updated}
        for name, status, updated in [("P", "Questionable", "2026-10-19"), ("P", "Out", "2026-10-20"),
                                      ("Q", "Active", "2026-10-20"), ("R", "Suspension", "2026-10-20")]]}]}
    rows = nfl.parse_injuries(payload, 2026)
    assert len(rows) == 1
    assert rows[0]["status"] == "Out"
    with pytest.raises(ValueError):
        nfl.parse_injuries(payload, 2025)
    assert nfl.parse_injuries({"season": {"year": 2026}, "injuries": []}, 2026) == []


def test_live_failure_is_not_zero_or_demo(monkeypatch):
    def fail(url):
        raise TimeoutError("offline")
    monkeypatch.setattr(nfl, "fetch_json", fail)
    result = nfl.load_live(2026)
    assert len(result["errors"]) == 3
    assert all(result[k] is None for k in ("teams", "quarterbacks", "injuries"))
    assert result["mode"] == "Live ESPN"


def test_partial_failure_preserves_available_data(monkeypatch):
    def fetch(url):
        if "injuries" in url:
            return {"season": {"year": 2026}, "injuries": []}
        raise ValueError("unavailable")
    monkeypatch.setattr(nfl, "fetch_json", fetch)
    result = nfl.load_live(2026)
    assert result["injuries"] == []
    assert set(result["errors"]) == {"teams", "quarterbacks"}


def test_season_rollover():
    assert nfl.season_year(date(2027, 1, 15)) == 2026
    assert nfl.season_year(date(2026, 10, 20)) == 2026


def test_chart_escapes_source_text():
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
    from nfl_chart import chart_html
    html = chart_html([{"label": "</script><script>alert(1)</script>", "value": 10}], "yards")
    assert "</script><script>alert(1)" not in html
    assert "\\u003c/script>" in html


def test_page_controls(monkeypatch):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
    from streamlit.testing.v1 import AppTest
    monkeypatch.setattr(nfl, "load_live", lambda year: nfl.load_demo(year))
    page = Path(__file__).resolve().parents[1] / "app/pages/5_NFL_Overview.py"
    app = AppTest.from_file(str(page)).run(timeout=30)
    assert not app.exception
    app.radio[0].set_value("Demo (fictional, offline)").run()
    assert app.metric[2].value == "8"
    for view in ("Teams", "Injuries", "Quarterbacks"):
        app.selectbox[0].set_value(view).run()
        assert not app.exception
        assert len(app.dataframe) >= 1
    app.slider[0].set_value(3).run()
    assert not app.exception


def test_page_unavailable_is_not_zero(monkeypatch):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
    import streamlit as st
    from streamlit.testing.v1 import AppTest
    st.cache_data.clear()
    def unavailable(year):
        return {"mode": "Live ESPN", "fetched_at": "test", "sources": {},
                "errors": {"injuries": "offline"}, "teams": None, "quarterbacks": None, "injuries": None}
    monkeypatch.setattr(nfl, "load_live", unavailable)
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app/pages/5_NFL_Overview.py")).run(timeout=30)
    assert not app.exception
    assert all(metric.value == "Unavailable" for metric in app.metric)
    app.selectbox[0].set_value("Injuries").run()
    assert not app.exception
    assert len(app.warning) == 1
    st.cache_data.clear()
