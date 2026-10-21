-- =============================================================
-- Database schema for the sports league.
-- Every table here matches a CSV file in data/raw/.
--
-- How the tables connect (this is what you JOIN on):
--
--   teams.team_id  <── players.team_id
--   teams.team_id  <── games.home_team_id / games.away_team_id
--   games.game_id  <── player_game_stats.game_id
--   players.player_id <── player_game_stats.player_id
-- =============================================================

DROP TABLE IF EXISTS player_game_stats;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS teams;

CREATE TABLE teams (
    team_id      INTEGER PRIMARY KEY,
    name         TEXT NOT NULL,
    city         TEXT NOT NULL,
    abbreviation TEXT NOT NULL
);

CREATE TABLE players (
    player_id INTEGER PRIMARY KEY,
    name      TEXT NOT NULL,
    team_id   INTEGER NOT NULL REFERENCES teams(team_id),
    position  TEXT NOT NULL            -- G (guard), F (forward), C (center)
);

CREATE TABLE games (
    game_id      INTEGER PRIMARY KEY,
    season       INTEGER NOT NULL,
    game_date    TEXT NOT NULL,        -- ISO format: YYYY-MM-DD
    home_team_id INTEGER NOT NULL REFERENCES teams(team_id),
    away_team_id INTEGER NOT NULL REFERENCES teams(team_id),
    home_score   INTEGER NOT NULL,
    away_score   INTEGER NOT NULL
);

-- One row per player per game ("box score" line).
CREATE TABLE player_game_stats (
    game_id   INTEGER NOT NULL REFERENCES games(game_id),
    player_id INTEGER NOT NULL REFERENCES players(player_id),
    team_id   INTEGER NOT NULL REFERENCES teams(team_id),
    minutes   INTEGER NOT NULL,
    points    INTEGER NOT NULL,
    rebounds  INTEGER NOT NULL,
    assists   INTEGER NOT NULL,
    PRIMARY KEY (game_id, player_id)
);
