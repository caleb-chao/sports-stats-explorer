"""🚧 TODO page. Step 1: write sql/team_standings.sql. Step 2: build the chart below."""

import streamlit as st

from common import run_query_or_todo

st.title("Standings")
st.write("What is every team's win-loss record?")

df = run_query_or_todo("team_standings")

if df is not None:
    st.dataframe(df, hide_index=True)
    # TODO: add a chart. Ideas:
    #   - bar chart of win_pct per team
    #   - scatter plot of point_diff vs win_pct (do teams that outscore
    #     opponents by more actually win more?)
