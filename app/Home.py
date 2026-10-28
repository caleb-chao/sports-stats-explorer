"""
Entry point for the dashboard. Run it with:

    streamlit run app/Home.py

Every file in app/pages/ automatically becomes a page in the sidebar.
"""

import streamlit as st

from common import ensure_database
from sports_stats.db import get_connection

st.set_page_config(page_title="Sports Stats Explorer", page_icon="🏀", layout="wide")
ensure_database()

st.title("🏀 Sports Stats Explorer")
st.write("Settling sports arguments with actual data. Pick a question from the sidebar.")
st.page_link("pages/5_NFL_Overview.py", label="NFL Overview — live stats and Three.js charts", icon="🏈")

# A few headline numbers, straight from SQL.
# TODO (good first task): move this query into sql/league_summary.sql and use run_query.
with get_connection() as conn:
    n_teams, n_players, n_games = conn.execute(
        "SELECT (SELECT COUNT(*) FROM teams), (SELECT COUNT(*) FROM players), (SELECT COUNT(*) FROM games)"
    ).fetchone()

c1, c2, c3 = st.columns(3)
c1.metric("Teams", n_teams)
c2.metric("Players", n_players)
c3.metric("Games played", n_games)

st.divider()
st.subheader("Questions this dashboard answers")
st.markdown(
    """
| Page | Question | Status |
|---|---|---|
| **Top Scorers** | Who scores the most points per game? | ✅ example |
| **Standings** | What's every team's record? | 🚧 TODO |
| **Close Games** | Which teams win close games? | 🚧 TODO |
| **Player Profile** | How has one player done game by game? | 🚧 TODO |
"""
)
st.caption("⚠️ Data is currently a fake sample league. See ROADMAP.md to swap in real data.")
