"""
Generate a FAKE sample league so the project works out of the box.

The data is random (but reproducible thanks to a fixed seed). It exists only so
everyone can start writing SQL and building charts on day one. Swapping it for
real data is one of the project tasks -- see ROADMAP.md.

Usage:
    python scripts/generate_sample_data.py
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
SEED = 42
SEASON = 2025
PLAYERS_PER_TEAM = 10

TEAMS = [
    ("Isla Vista", "Surfers", "IVS"),
    ("Goleta", "Gulls", "GOL"),
    ("Santa Barbara", "Sunsets", "SBS"),
    ("Ventura", "Vipers", "VEN"),
    ("San Luis Obispo", "Stallions", "SLO"),
    ("Oxnard", "Orcas", "OXN"),
    ("Carpinteria", "Comets", "CAR"),
    ("Lompoc", "Lynx", "LOM"),
]

FIRST_NAMES = [
    "Alex", "Jordan", "Taylor", "Sam", "Chris", "Morgan", "Jamie", "Riley",
    "Casey", "Drew", "Avery", "Quinn", "Reese", "Skyler", "Devin", "Rowan",
]
LAST_NAMES = [
    "Garcia", "Nguyen", "Smith", "Patel", "Kim", "Lopez", "Johnson", "Chen",
    "Brown", "Martinez", "Davis", "Singh", "Wilson", "Lee", "Moore", "Clark",
]
POSITIONS = ["G", "G", "G", "F", "F", "F", "C", "C", "G", "F"]


def write_csv(path: Path, header: list[str], rows: list[tuple]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"  wrote {len(rows):>5} rows -> {path.relative_to(RAW_DIR.parent.parent)}")


def main() -> None:
    rng = random.Random(SEED)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # --- teams -------------------------------------------------------------
    teams = [(i + 1, f"{city} {mascot}", city, abbr) for i, (city, mascot, abbr) in enumerate(TEAMS)]

    # --- players -----------------------------------------------------------
    # Each player gets a hidden "skill" that controls how many points they score.
    players, skill = [], {}
    used_names = set()
    player_id = 1
    for team_id, *_ in teams:
        for slot in range(PLAYERS_PER_TEAM):
            name = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
            while name in used_names:
                name = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
            used_names.add(name)
            players.append((player_id, name, team_id, POSITIONS[slot]))
            # Starters (first 5 slots) play more and score more.
            skill[player_id] = rng.uniform(0.8, 1.4) if slot < 5 else rng.uniform(0.3, 0.8)
            player_id += 1

    # --- games + box scores -----------------------------------------------
    # Double round robin: every team hosts every other team once.
    matchups = [(h[0], a[0]) for h in teams for a in teams if h[0] != a[0]]
    rng.shuffle(matchups)

    games, box_scores = [], []
    game_day = date(SEASON, 10, 20)
    for game_id, (home_id, away_id) in enumerate(matchups, start=1):
        scores = {}
        for team_id in (home_id, away_id):
            total = 0
            for pid, _, p_team, _ in players:
                if p_team != team_id:
                    continue
                s = skill[pid]
                minutes = max(0, int(rng.gauss(30 * s, 5)))
                points = max(0, int(rng.gauss(minutes * 0.5 * s, 4)))
                if team_id == home_id:  # small home-court advantage
                    points += rng.choice([0, 0, 1])
                rebounds = max(0, int(rng.gauss(minutes * 0.15, 2)))
                assists = max(0, int(rng.gauss(minutes * 0.1, 1.5)))
                box_scores.append((game_id, pid, team_id, minutes, points, rebounds, assists))
                total += points
            scores[team_id] = total

        # Basketball has no ties: give a random player on one team a bonus point.
        if scores[home_id] == scores[away_id]:
            winner = rng.choice([home_id, away_id])
            for i in range(len(box_scores) - 1, -1, -1):
                g, pid, t, m, pts, r, a = box_scores[i]
                if t == winner:
                    box_scores[i] = (g, pid, t, m, pts + 1, r, a)
                    break
            scores[winner] += 1

        games.append((game_id, SEASON, game_day.isoformat(), home_id, away_id,
                      scores[home_id], scores[away_id]))
        game_day += timedelta(days=rng.choice([1, 2, 3]))

    print(f"Generating sample data in {RAW_DIR} (seed={SEED})")
    write_csv(RAW_DIR / "teams.csv", ["team_id", "name", "city", "abbreviation"], teams)
    write_csv(RAW_DIR / "players.csv", ["player_id", "name", "team_id", "position"], players)
    write_csv(RAW_DIR / "games.csv",
              ["game_id", "season", "game_date", "home_team_id", "away_team_id", "home_score", "away_score"],
              games)
    write_csv(RAW_DIR / "player_game_stats.csv",
              ["game_id", "player_id", "team_id", "minutes", "points", "rebounds", "assists"],
              box_scores)


if __name__ == "__main__":
    main()
