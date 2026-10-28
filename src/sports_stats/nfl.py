"""Small ESPN adapter. Never substitute demo or a different season for live data."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import math
from urllib.request import Request, urlopen


INJURY_STATUSES = {"Questionable", "Doubtful", "Out", "Injured Reserve", "IR", "Physically Unable to Perform", "PUP"}


def season_year(today=None):
    today = today or datetime.now(timezone.utc).date()
    return today.year - (today.month < 3)


def source_urls(season):
    return {
        "teams": f"https://site.api.espn.com/apis/v2/sports/football/nfl/standings?season={season}&seasontype=2",
        "quarterbacks": f"https://site.api.espn.com/apis/site/v3/sports/football/nfl/leaders?season={season}&seasontype=2",
        "injuries": "https://site.api.espn.com/apis/site/v2/sports/football/nfl/injuries",
    }


def fetch_json(url):
    with urlopen(Request(url, headers={"User-Agent": "SportsStatsExplorer/1.0"}), timeout=15) as response:
        return json.load(response)


def number(value):
    result = float(value)
    if not math.isfinite(result) or result < 0:
        raise ValueError("Invalid statistic in source")
    return result


def parse_teams(payload, season):
    rows = {}

    def visit(node):
        standings = node.get("standings", {})
        if standings.get("entries"):
            if int(standings.get("season", 0)) != season or int(standings.get("seasonType", 0)) != 2:
                raise ValueError("Standings season does not match requested regular season")
            for entry in standings["entries"]:
                team = entry["team"]
                stats = {s["name"]: s.get("value") for s in entry["stats"]}
                wins, losses, ties = (int(number(stats[k])) for k in ("wins", "losses", "ties"))
                games = wins + losses + ties
                rows[team["id"]] = {"team": team["displayName"], "wins": wins, "losses": losses,
                    "ties": ties, "win_pct": (wins + ties / 2) / games if games else 0,
                    "point_diff": number(stats["pointsFor"]) - number(stats["pointsAgainst"])}
        for child in node.get("children", []):
            visit(child)

    visit(payload)
    if not rows:
        raise ValueError("No standings available")
    return sorted(rows.values(), key=lambda r: (-r["win_pct"], -r["point_diff"], r["team"]))


def parse_quarterbacks(payload, season):
    requested = payload.get("requestedSeason", {})
    if int(requested.get("year", 0)) != season or int(requested.get("type", {}).get("type", 0)) != 2:
        raise ValueError("Quarterback feed does not match requested regular season")
    rows = {}
    for category in payload["leaders"]["categories"]:
        if category["name"] != "passingYards":
            continue
        for entry in category["leaders"]:
            athlete = entry["athlete"]
            if athlete.get("position", {}).get("abbreviation") == "QB":
                rows[athlete["id"]] = {"player": athlete["displayName"],
                    "team": entry["team"]["displayName"], "passing_yards": number(entry["value"])}
    if not rows:
        raise ValueError("No quarterback passing leaders available")
    return sorted(rows.values(), key=lambda r: (-r["passing_yards"], r["player"]))


def parse_injuries(payload, season):
    if int(payload.get("season", {}).get("year", 0)) != season:
        raise ValueError("Injury feed season does not match; historical injuries are unavailable")
    if not isinstance(payload.get("injuries"), list):
        raise ValueError("Injury report missing")
    rows = {}
    for team in payload["injuries"]:
        for injury in team["injuries"]:
            if injury.get("status") not in INJURY_STATUSES:
                continue
            athlete = injury["athlete"]
            key = athlete.get("id") or (team["id"], athlete["displayName"])
            row = {"player": athlete["displayName"], "team": team["displayName"],
                "status": injury["status"], "updated": injury.get("date", "Unknown")}
            if key not in rows or row["updated"] > rows[key]["updated"]:
                rows[key] = row
    return sorted(rows.values(), key=lambda r: (r["team"], r["player"]))


def load_live(season):
    parsers = {"teams": parse_teams, "quarterbacks": parse_quarterbacks, "injuries": parse_injuries}
    urls = source_urls(season)
    result = {"season": season, "mode": "Live ESPN", "fetched_at": datetime.now(timezone.utc).isoformat(),
              "sources": urls, "errors": {}}
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {key: pool.submit(fetch_json, url) for key, url in urls.items()}
        for key, future in futures.items():
            try:
                payload = future.result()
                result[key] = parsers[key](payload, season)
                if key == "injuries":
                    result["injuries_updated"] = payload.get("timestamp", "Not supplied")
            except Exception as exc:
                result[key] = None
                result["errors"][key] = f"{type(exc).__name__}: {exc}"
    return result


def load_demo(season):
    """Deliberately fictional names and values, for an offline presentation."""
    return {"season": season, "mode": "DEMO — fictional data", "fetched_at": "Not applicable (synthetic)",
        "sources": {}, "errors": {}, "injuries_updated": "Not applicable (synthetic)",
        "teams": [{"team": f"Demo Team {i+1}", "wins": 6-i, "losses": i, "ties": 0,
                   "win_pct": (6-i)/6, "point_diff": 60-i*15} for i in range(6)],
        "quarterbacks": [{"player": f"Demo QB {i+1}", "team": f"Demo Team {i+1}",
                          "passing_yards": 1800-i*125} for i in range(6)],
        "injuries": [{"player": f"Demo Player {i+1}", "team": f"Demo Team {i//2+1}",
                      "status": "Out" if i%2 else "Questionable", "updated": "Synthetic"} for i in range(8)]}
