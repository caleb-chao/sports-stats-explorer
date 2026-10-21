"""🚧 TODO page. Step 1: write sql/player_profile.sql. Step 2: build the chart below."""

import streamlit as st

from common import run_query_or_todo

st.title("Player Profile")
st.write("How has a player performed game by game?")

# TODO: replace this text box with a dropdown (st.selectbox) of every player.
#       Hint: you'll need a small query that lists player names.
player_name = st.text_input("Player name", "")

if player_name:
    df = run_query_or_todo("player_profile", {"player_name": player_name})
    if df is not None:
        st.dataframe(df, hide_index=True)
        # TODO: line chart of points over time (px.line with x="game_date", y="points")
