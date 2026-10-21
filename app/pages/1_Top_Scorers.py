"""
✅ WORKED EXAMPLE PAGE -- copy this pattern for new pages.

The pattern is always:
  1. Widgets (sliders, dropdowns) to pick parameters
  2. run_query_or_todo("<sql file name>", {params})  ->  a pandas DataFrame
  3. Show it: a chart + the raw table
"""

import plotly.express as px
import streamlit as st

from common import run_query_or_todo

st.title("Top Scorers")
st.write("Who scores the most points per game?")

# 1. Inputs
col1, col2 = st.columns(2)
limit = col1.slider("How many players", 5, 25, 10)
min_games = col2.slider("Minimum games played", 1, 14, 5)

# 2. Query
df = run_query_or_todo("top_scorers", {"limit": limit, "min_games": min_games})

# 3. Display
if df is not None:
    fig = px.bar(
        df.sort_values("points_per_game"),
        x="points_per_game",
        y="player",
        color="team",
        orientation="h",
        labels={"points_per_game": "Points per game", "player": ""},
    )
    st.plotly_chart(fig)

    with st.expander("See the data"):
        st.dataframe(df, hide_index=True)
