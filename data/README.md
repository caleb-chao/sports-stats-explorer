# Data

`raw/` holds one CSV per database table. Column names must match `db/schema.sql`.

| File | One row per… |
|---|---|
| `teams.csv` | team |
| `players.csv` | player (with the team they play for) |
| `games.csv` | game (home team, away team, final score) |
| `player_game_stats.csv` | player per game (box score line: minutes, points, rebounds, assists) |

**The current data is fake.** It was made by `scripts/generate_sample_data.py` so
everyone can start immediately. Replacing it with a real league is a project task
(see `ROADMAP.md`). When you do, write a script in `scripts/` that downloads/cleans
the real data and writes CSVs in this same shape, then run `python scripts/load_data.py`.
