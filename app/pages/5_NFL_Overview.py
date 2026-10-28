"""Issue #1: current-season NFL stakeholder dashboard."""
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from common import ROOT  # adds src/ to the import path
from nfl_chart import chart_html
from sports_stats.nfl import INJURY_STATUSES, load_demo, load_live, season_year

st.set_page_config(page_title="NFL Overview", page_icon="🏈", layout="wide")
st.title("🏈 NFL season overview")
st.write("Quarterback production, team performance, and the current injury report.")
mode = st.radio("Data source", ["Live ESPN", "Demo (fictional, offline)"], horizontal=True)
season = season_year()
st.caption(f"{season} regular season · rankings reflect the records returned by the provider")


@st.cache_data(ttl=900, show_spinner=False)
def cached_live(year):
    return load_live(year)


if st.button("Refresh live data", disabled=mode != "Live ESPN"):
    cached_live.clear()
with st.spinner("Loading NFL statistics…"):
    data = cached_live(season) if mode == "Live ESPN" else load_demo(season)
if mode != "Live ESPN":
    st.warning("DEMO — fictional players, teams, and numbers. Not current NFL statistics.")
st.caption(f"Source: {data['mode']} · retrieved: {data['fetched_at']} · live cache: 15 minutes")
for key, error in data["errors"].items():
    st.warning(f"{key.title()} unavailable. Refresh to retry, or choose the labeled demo mode. {error}")

qbs, teams, injuries = (data.get(k) for k in ("quarterbacks", "teams", "injuries"))
cols = st.columns(3)
cols[0].metric("Passing-yard leader", qbs[0]["player"] if qbs else "Unavailable")
team_leader = teams[0]["team"] if teams else "Unavailable"
if teams and not any(r["wins"] + r["losses"] + r["ties"] for r in teams):
    team_leader = "No games played"
cols[1].metric("Top team by win percentage", team_leader)
cols[2].metric("Players on injury report", len(injuries) if injuries is not None else "Unavailable")
st.caption("Tied passing totals share the lead. Teams use point differential to break equal win percentages; this is not official playoff seeding.")

view = st.selectbox("Visualization", ["Quarterbacks", "Teams", "Injuries"])
limit = st.slider("Bars to display", 3, 10, 10)
if view == "Quarterbacks":
    st.subheader("Leading quarterbacks · passing yards")
    st.write("‘Best’ here means most total passing yards, not an overall skill rating. Only the provider's returned passing leaders are included.")
    records, label, value, unit = qbs, "player", "passing_yards", "passing yards"
elif view == "Teams":
    st.subheader("Team standings · win percentage")
    st.write("Win percentage = (wins + 0.5 × ties) / games played. Zero-game teams show 0%; no leader is established until games are played.")
    records = None if teams is None else [dict(r, win_percentage=round(r["win_pct"]*100, 2)) for r in teams]
    label, value, unit = "team", "win_percentage", "% wins"
else:
    st.subheader("Current reported injuries · players per team")
    st.write("Unique players with injury designations in the current feed. This is not the number of injury events during the season. Active news and suspensions are excluded; missing teams are not assumed to have zero injuries.")
    st.caption(f"Included statuses: {', '.join(sorted(INJURY_STATUSES))}. Feed timestamp: {data.get('injuries_updated', 'Unavailable')}")
    records = None
    if injuries is not None:
        counts = {}
        for injury in injuries:
            counts[injury["team"]] = counts.get(injury["team"], 0) + 1
        records = sorted([{"team": team, "players": count} for team, count in counts.items()], key=lambda r: (-r["players"], r["team"]))
    label, value, unit = "team", "players", "reported players"

if records:
    html = chart_html([{"label": r[label], "value": r[value]} for r in records[:limit]], unit)
    if hasattr(st, "iframe"):
        st.iframe(html, height=570, alt=f"NFL {view.lower()} bar chart")
    else:  # Compatibility with the project's Streamlit 1.38 minimum.
        components.html(html, height=570, scrolling=True)
    st.caption(f"Showing {min(limit, len(records))} of {len(records)} returned rows. Full data below.")
    frame = pd.DataFrame(records)
    st.dataframe(frame, hide_index=True)
    st.download_button("Download displayed dataset (CSV)", frame.to_csv(index=False), f"nfl_{view.lower()}_{season}.csv", "text/csv")
elif records is not None:
    st.info("No matching records reported. An empty feed does not establish that the league has no injuries.")
if view == "Injuries" and injuries:
    with st.expander("Individual injury records"):
        st.dataframe(pd.DataFrame(injuries), hide_index=True)
with st.expander("Sources and limitations"):
    st.write("ESPN public endpoints are unofficial integration interfaces and can change or be unavailable. Retrieval time is not a guarantee of when each statistic was updated. Injury reporting coverage may be incomplete.")
    for name, url in data["sources"].items():
        st.markdown(f"[{name.title()} source]({url})")
