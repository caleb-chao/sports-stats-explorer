"""🚧 TODO page. Step 1: write sql/close_games.sql. Step 2: build the chart below."""

import streamlit as st

from common import run_query_or_todo

st.title("Close Games")
st.write("Which teams win when the game is close?")

margin = st.slider("A game is 'close' if decided by this many points or fewer", 1, 10, 5)

df = run_query_or_todo("close_games", {"margin": margin})

if df is not None:
    st.dataframe(df, hide_index=True)
    # TODO: add a chart. Ideas:
    #   - bar chart of close_win_pct per team
    #   - compare close-game win % against overall win % (from team_standings)
