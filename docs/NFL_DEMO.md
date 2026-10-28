# NFL overview: test and present today

Implements issue #1 inside the existing Streamlit app. No Node build or API key is needed.

## Windows / PowerShell

From the repository root (Python 3.12 recommended):

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app/Home.py
```

If `.venv` is already set up, skip the first two commands. Using the explicit
interpreter avoids PowerShell activation policy and PATH issues.

Open **http://localhost:8501/NFL_Overview**, or choose **NFL Overview** in the
sidebar. The NFL page does not require loading the basketball database. The Home
page builds that separate database automatically from the existing CSV files.
Stop the server with Ctrl+C.

On macOS/Linux use `python3 -m venv .venv` and `.venv/bin/python` in place of
`.\.venv\Scripts\python.exe`.

## Five-minute stakeholder demo

1. Open NFL Overview in **Live ESPN** mode. Check the season, retrieval timestamp,
   and any warnings before presenting. Click **Refresh live data** once.
2. Explain the three cards: passing-yard leader, top team by win percentage,
   and unique players currently carrying an injury designation.
3. On **Quarterbacks**, hover over a bar, drag to rotate, use **Inspect bar**
   with the keyboard, and click **Reset view**. Compare the values to the table.
4. Switch **Visualization** to **Teams**, then **Injuries**. Adjust **Bars to
   display**. Open individual injury records and download the CSV.
5. If feeds fail, explicitly select **Demo (fictional, offline)**. State that
   these are synthetic numbers demonstrating functionality. Three.js is
   bundled locally, so demo charts need no CDN connection.

For a live presentation today, run the app locally and screen-share the browser.
`localhost` is only accessible on your computer; it is not a public deployment.

## End-to-end acceptance checklist

- All three views render bars with readable names, exact values, and units.
- Changing the bar count changes the chart but retains the full source table.
- Hover/Inspect bar identifies the right row; rotation and reset work.
- CSV values match the full displayed dataset (not just the top N bars).
- Live source links, season, and timestamps are visible. Quarterback results
  include only QB positions among the provider's returned passing leaders.
- Team ordering uses `(wins + ties / 2) / games`, then point differential.
  Equal values are not represented as official playoff tiebreakers.
- Injury totals match the individual records. Active news and suspensions
  are excluded. Counts represent current reports, not cumulative injuries.
- Select demo mode and verify a conspicuous fictional-data warning.
- To test a provider outage, disconnect networking, select live mode, then
  click refresh: unavailable feeds show warnings and **Unavailable**, not 0.
  Reconnect and refresh to recover. Other successful feeds remain usable.
- At a narrow browser width, controls and the data remain usable.
- With WebGL disabled, the chart explains the limitation and the data table
  and CSV remain available.

## Optional automated browser check

Keep Streamlit running in one terminal. In a second terminal:

```powershell
.\.venv\Scripts\python.exe -m pip install playwright
.\.venv\Scripts\python.exe scripts/test_nfl_browser.py --browser-channel chrome
```

Alternatively run `python -m playwright install chromium` using your virtual
environment, then omit `--browser-channel chrome`. This optional dependency is
not required for deploying or using the dashboard. Screenshots go to `artifacts/`.
The smoke test exercises demo-mode WebGL rendering and controls. Live provider
availability must be checked separately; deterministic pytest tests use fixtures.

## Data and maintenance notes

- Live data comes from ESPN's public JSON endpoints, linked in the page. These
  are unofficial integration interfaces with no availability guarantee.
- Rankings use the current NFL season (January/February belong to the previous
  calendar year's season). Only regular-season rankings are requested.
- The source may return a limited leaderboard (currently ten passing leaders),
  not every QB. The UI shows the number of returned rows.
- Source season mismatches and malformed records produce an unavailable state.
  The app never silently substitutes another season or fictional data.
- Successful and failed responses are cached for 15 minutes. Refresh clears
  the cache. Retrieval time is not the provider's per-stat update time.
- The injury feed's timestamp is shown separately. Missing teams do not imply
  zero injuries. Statuses and coverage depend on the provider.
- `app/assets/three.min.js` is Three.js **0.160.1**, distributed under the
  accompanying MIT license. It is vendored to make the demo independent of CDNs.
- The renderer uses `st.iframe` when available, with the v1 HTML iframe API
  as a compatibility fallback for the project's older Streamlit minimum.
